from sqlalchemy import or_

from flask import Flask
from flask_cors import CORS, cross_origin
from database.Database import get_session, Commit, Project, Page, Diff, PageContent
from json import dumps
import html_diff.HtmlUtils as HtmlUtils

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

DB = get_session()

@app.route("/projects")
@cross_origin()
def get_projects():

    projects = DB.query(Project).all()

    projects = list(map(lambda x: {
        "id": x.id,
        "name": x.name
    }, projects))

    return dumps(projects)


@app.route("/projects/<id>")
@cross_origin()
def get_project_commits(id):
    commits = DB.query(Commit).filter(Commit.project_id == id, Commit.pages.any()).order_by(Commit.timestamp.asc()).all()

    commits = list(map(lambda x: {
        "id": x.id,
        "hash": x.hash
    }, commits))

    return dumps(commits[1:])

@app.route("/commits/<id>")
@cross_origin()
def get_sitemap(id):
    first_page = DB.query(Page) \
        .filter(Page.commit_id == id) \
        .order_by(Page.added_at) \
        .limit(1) \
        .all()

    if not first_page:
        return dumps([])

    print(first_page[0].commit_id)

    current_commit = DB.query(Commit).filter(Commit.id == first_page[0].commit_id).first()
    print(current_commit)
    print(current_commit.timestamp)

    previous_commit = DB.query(Commit).filter(Commit.timestamp < current_commit.timestamp).order_by(Commit.timestamp.desc()).first()

    previous_pages = DB.query(Page).filter(Page.commit_id == previous_commit.id).all()


    processed = []
    pages = []
    links = []

    def helper(page):
        links.extend([{
            "id": "l" + str(page.id) + str(x.id),
            "source": "p" + str(page.id),
            "target": "p" + str(x.id)
        } for x in page.to_page])

        diffs = DB.query(Diff).filter(Diff.page_new_id == page.id).all()

        diffs = list(filter(
            lambda x: "head" not in x.element and (x.new_screenshot or x.old_screenshot or x.new_html or x.old_html),
            diffs))

        page_diffs = []
        action_diffs = []

        for diff in diffs:
            if diff.action is None:
                page_diffs.append(diff)

        for diff in diffs:
            if diff.action is not None:
                found = next((x for x in page_diffs if
                              x.element == diff.element and x.old_html == diff.old_html and x.new_html == diff.new_html),
                             None)
                if not found:
                    action_diffs.append(diff)

        diffs = len(page_diffs + action_diffs)

        color = "white"
        disabled = True

        if diffs > 0:
            color = "#ffadad"
            disabled = False

        # page is new
        if next((x for x in previous_pages if x.url == page.url), None) is None:
            color = "#6dff81"
            disabled = True

        pages.append({
            "id": "p" + str(page.id),
            "label": page.url,
            "color": color,
            "diffs": diffs,
            "disabled": disabled
        })
        processed.append(page.id)

        if not page.to_page:
            return

        for child in page.to_page:
            if child.id not in processed:
                helper(child)

    helper(first_page[0])

    for old_page in previous_pages:
        if next((x for x in pages if x["label"] == old_page.url), None) is None:
            pages.append({
                "id": "p" + str(old_page.id),
                "label": old_page.url,
                "color": "#adadad",
                "diffs": 0,
                "disabled": True
            })

    return dumps({
        "pages": pages,
        "links": links
    })

@app.route("/pages/<id>")
@cross_origin()
def get_diffs(id):

    id = id.replace("p", "")

    diffs = DB.query(Diff).filter(Diff.page_new_id == id).all()

    diffs = list(filter(lambda x: "head" not in x.element and (x.new_screenshot or x.old_screenshot or x.new_html or x.old_html), diffs))

    page_diffs = []
    action_diffs = []

    for diff in diffs:
        if diff.action is None:
            page_diffs.append(diff)

    for diff in diffs:
        if diff.action is not None:
            found = next((x for x in page_diffs if x.element == diff.element and x.old_html == diff.old_html and x.new_html == diff.new_html), None)
            if not found:
                action_diffs.append(diff)


    diffs = list(map(lambda x: {
        "id": x.id,
        "action": x.action.type if x.action else None,
        "action_element": x.action.element if x.action else None,
        "element": x.element,
        "old_screenshot": x.old_screenshot,
        "new_screenshot": x.new_screenshot,
        "old_html": normal_html(x.old_html) if x.old_html else x.old_html,
        "new_html": normal_html(x.new_html) if x.new_html else x.new_html
    }, page_diffs + action_diffs))

    for diff in diffs:
        diff["old_html"] = diff["old_html"].replace("https://fri.uni-lj.si", "http://www.fri.uni-lj.si").replace(
            "https://www.fri.uni-lj.si", "http://www.fri.uni-lj.si")
        diff["new_html"] = diff["new_html"].replace("https://fri.uni-lj.si", "http://www.fri.uni-lj.si").replace("https://www.fri.uni-lj.si", "http://www.fri.uni-lj.si")

    diffs = list(filter(lambda x: x["new_html"] != x["old_html"], diffs))

    return dumps(diffs)

def normal_html(html):
    return HtmlUtils.normalize_result_html(html, True).prettify()




