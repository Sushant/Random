#!python2.6

import sys
import urllib
import time
import httplib2
import json


class GSRequest:
  """Class that handles all the API requests to Github, performs some
  manipulations on the received responses.

  :param str cache: optional location of directory to store http cache
  """
  def __init__(self, cache='.cache'):
    github_url = 'https://github.com/api'
    api_version = 'v2'
    api_format = 'json'

    self.base_url = '/'.join([github_url, api_version, api_format])
    self.req_limit = 1
    self.last_request = 0
    self.client = httplib2.Http(cache=cache)


  def perform_request(self, type, method, param):
    param = urllib.quote(param)
    url = '/'.join([self.base_url, type, method, param])
    time_diff = time.time() - self.last_request
    if time_diff < self.req_limit:
      time.sleep(self.req_limit - time_diff)

    try:
      response, content = self.client.request(url)
      if response.status >= 400:
        print 'Unable to perform request %s. Error %s' % (url, str(response))
        sys.exit(1)
      self.last_request = time.time()
      result = json.loads(content.decode('utf-8'))
      return result
    except Exception as fault:
      print 'Unable to perform request %s. Error %s' % (url, str(fault))
      sys.exit(1)


  def search_project(self, project_name):
    result = self.perform_request('repos', 'search', project_name)
    repo = result['repositories']
    if repo:
      return repo[0]
    return None


  def get_project_members(self, project_name, project_owner):
    result = self.perform_request('repos', 'show', \
               '/'.join([project_owner, project_name, 'network']))
    forks = result['network']
    member_list = []
    for f in forks:
      member_list.append(f['owner'])
    return member_list


  def get_member_repos(self, member_id, relevant_languages):
    result = self.perform_request('repos', 'show', member_id)
    repos = result['repositories']

    authored = 0
    forked = 0
    relevant = 0

    for repo in repos:
      if 'language' in repo and repo['language'] in relevant_languages:
        relevant += 1
      if not repo['fork']:
        authored += 1
      else:
        forked += 1
    return {'login': member_id,
            'authored': authored,
            'relevant': relevant,
            'forked': forked,
            'total': authored + forked}


  def get_member_info(self, member_dict):
    result = self.perform_request('user', 'show', member_dict['login'])
    member_info = result['user']
    member_dict['name'] = ''
    member_dict['blog'] = ''
    member_dict['email'] = ''
    if 'name' in member_info and member_info['name']:
      member_dict['name'] = member_info['name']
    if 'email' in member_info and member_info['email']:
      member_dict['email'] = member_info['email']
    if 'blog' in member_info and member_info['blog']:
      member_dict['blog'] = member_info['blog']
    member_dict['gravatar'] = member_info['gravatar_id']
    return member_dict



class GitSucker:
  """GitSucker class

  :param str project_name: project to be searched
  :param list relevant_languages: languages relevant to hiring position e.g.
                                  ['Ruby', 'Javascript']
  :param int candidate_count: number of candidates to be shortlisted
  """

  def __init__(self, project_name, relevant_languages, candidate_count):
    self.request = GSRequest()
    self.project_name = project_name
    self.relevant_languages = relevant_languages
    self.candidate_count = candidate_count


  def run(self):
    """Driver function
    
    :return list of dicts with info of shortlisted candidates
    """
    print '[INFO] Searching Github for project %s ...' % self.project_name
    project = self.request.search_project(self.project_name)
    if not project:
      print '[ERROR] Found no projects matching \'%s\'' % self.project_name
      sys.exit(1)
    print '[INFO] Fetching list of project members ...'
    member_list = self.request.get_project_members(project['name'],
                    project['owner'])
    print '[INFO] Found %d member(s) working on %s' % (len(member_list),
    self.project_name)
    print '[INFO] Gathering repository information of project member(s) ...'
    filtered_member_list = self._filter_members(member_list)
    print '[INFO] Gathering information of short listed member(s) ...'
    final_member_list = self._get_members_info(filtered_member_list)
    return final_member_list


  def _filter_members(self, member_list):
    filtered_member_list = []
    for member_id in member_list:
      member_dict = self.request.get_member_repos(member_id, self.relevant_languages)

      filtered_member_list.append(member_dict)
      if len(filtered_member_list) > self.candidate_count:
        filtered_member_list = self._sort_members(filtered_member_list)
        filtered_member_list.pop()

    if len(filtered_member_list) < self.candidate_count:
      filtered_member_list = self._sort_members(filtered_member_list)

    return filtered_member_list

  # Sort members based on number of authored, relevant and total repositories
  def _sort_members(self, member_list):
    sorted_member_list = sorted(member_list,
                                 key=lambda k: (k['authored'],
                                                k['relevant'],
                                                k['authored'] + k['forked']),
                                 reverse=True)
    return sorted_member_list


  def _get_members_info(self, member_list):
    final_member_list = []
    for member in member_list:
      member_dict = self.request.get_member_info(member)
      final_member_list.append(member_dict)
    return final_member_list



class HTMLResponse:
  """Class to generate an HTML Response from the list of dicts object returned
  by GitSucker

  :param list member_list: list of dicts of member information
  :param str project_name: used for naming the html file
  """


  def __init__(self, member_list, project_name):
    self.member_list = member_list
    self.project_name = project_name
    self.base_html = """
    <html>
      <head>
        <link href="../media/gitsucker.css" rel="stylesheet" type="text/css" />
      </head>
      <body>
        <div class="header">GitSucker: %s</div>
        %s
      </body>
    </html>
    """


  def format_response(self):
    """Generates an html file from member information
    File is placed in projects folder as <project_name>.html
    
    .. note:: Opens the html file default web browser
    """

    import os
    import codecs
    import webbrowser

    container = ''
    for member_dict in self.member_list:
      member_div = self._render_member_div(member_dict)
      container += member_div
    html_string = self.base_html % (self.project_name, container)
    html_file_name = 'projects/' + self.project_name + '.html'
    html_file = codecs.open(html_file_name, 'w', 'utf-8')
    html_file.write(html_string)
    file_url = os.path.join('file://', os.getcwd(), html_file_name)
    webbrowser.open(file_url)


  def _render_member_div(self, member_dict):
    image_div = self._render_image_div(member_dict['gravatar'])
    repo_div = self._render_repo_div(member_dict)
    info_div = self._render_info_div(member_dict)
    member_div = '<div class="candidate">' + image_div + repo_div + \
                   info_div + '</div>'
    return member_div


  def _render_image_div(self, gravatar_id):
    image_div = """
      <div class='image_div' style="background-image:
      url(http://www.gravatar.com/avatar/%s)"></div>""" % gravatar_id
    return image_div


  def _render_repo_div(self, member_dict):
    repo_div = """
      <div class="repo_count">
        <div class="authored" title="Authored Repositories">
          <img class="icon" src="../media/authored.png" />%d</div>
        <div class="relevant" title="Relevant Repositories">
          <img class="icon" src="../media/relevant.png">%d</div>
        <div class="forked" title="Forked Repositories">
          <img class="icon" src="../media/fork.png">%d</div>
      </div>

    """ % (member_dict['authored'], member_dict['relevant'], member_dict['forked'])
    return repo_div


  def _render_info_div(self, member_dict):
    info_div = """
      <div class='info_div'>
        <div class="txt" style="font-weight:bold;">%(name)s</div>
        <div class="txt"><a href="http://github.com/%(login)s">%(login)s</a></div>
        <div class="txt"><a href="mailto:%(email)s">%(email)s</a></div>
        <div class="txt"><a href="%(blog)s">%(blog)s</a></div>
      </div>
    """ % {'name': member_dict['name'],
           'login': member_dict['login'],
           'email': member_dict['email'],
           'blog': member_dict['blog']
    }
    return info_div



if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'Usage: python %s <project_name>' % (sys.argv[0])
    sys.exit(1)

  project_name = sys.argv[1]
  gs = GitSucker(project_name, ['Ruby', 'Javascript'], 21)
  final_member_list = gs.run()
  response_obj = HTMLResponse(final_member_list, project_name)
  response_obj.format_response()
