from sqlalchemy import or_
from database.Database import get_session, Page, Commit, Project, Diff
from project.ProjectConfig import ProjectConfig
from project.Config import Config
from typing import List
from graphviz import Digraph
from base64 import decodebytes



def truncate(value: str, length=500, n=50) -> str:
    value = "\n".join(value[i:i+n] for i in range(0, len(value), n))
    return value[:length] + (value[length:] and '...')

def save_temp_image(value: str, name: str):
    with open(name, "wb") as file:
        file.write(decodebytes(value.encode("utf8")))

def get_html_image(value: str):
    return f"<<TABLE STYLE=\"border: none;\"><TR><TD><IMG SRC=\"{value}\"/></TD></TR></TABLE>>"
    #return f"""<<TABLE><TR><TD><IMG src="data:image/png;base64,{value}" /></TD></TR></Table>>"""

def table():
    return "<<TABLE cellspacing=\"0\">"

def _table():
    return "</TABLE>>"

def tr():
    return "<TR>"

def _tr():
    return "</TR>"

def td(value):
    return f"<TD>{value}</TD>"

def get_record(element, image1, image2):
    #<<TABLE>
    return f"""
    <TR><TD>{element}</TD>
    <TD><IMG SRC=\"{image1}\"/></TD>
    <TD><IMG SRC=\"{image2}\"/></TD></TR>
    """
    #</TABLE>>
    #return f"{{ {element} | {image1} | {image2} }}"

class Result:

    def __init__(self, project_config: ProjectConfig, old_commit: str, new_commit: str):
        self.db = get_session(True)
        self.project_config = project_config
        self.old_commit = old_commit
        self.new_commit = new_commit
        self.old_processed_pages = []
        self.new_processed_pages = []


    def get_sitemap(self):
        initial_pages = self.get_initial_pages()
        old_page, old_commit  = next((x for x in initial_pages if x[1].hash == self.old_commit), initial_pages[0])
        new_page, new_commit = next((x for x in initial_pages if x[1].hash == self.new_commit), initial_pages[1])




        def sitemap_helper(page: Page, processed_pages: List[int], graph: Digraph):
            processed_pages.append(page.id)
            diffs = self.db.query(Diff).filter(or_(Diff.page_old_id == page.id, Diff.page_new_id == page.id)).distinct(Diff.id).all()

            record = table()
            record += tr() + td(truncate(page.url)) + _tr()

            for diff in diffs:
                save_temp_image(diff.old_screenshot, f"diff_old_screen_{diff.id}.png")
                save_temp_image(diff.new_screenshot, f"diff_new_screen_{diff.id}.png")
                record += get_record(diff.element, f"diff_old_screen_{diff.id}.png", f"diff_new_screen_{diff.id}.png")

            record += _table()

            graph.node(f"page{page.id}", record, shape="rectangle", margin="0")

            if not page.to_page:
                return

            for child_page in page.to_page:
                graph.edge(f"page{page.id}", f"page{child_page.id}")
                if child_page.id not in processed_pages:
                    sitemap_helper(child_page, processed_pages, graph)

        #old_dot = Digraph("OldSitemap", graph_attr={'rankdir':'LR'})
        new_dot = Digraph("NewSitemap", graph_attr={'rankdir':'LR'})

        #sitemap_helper(old_page, self.old_processed_pages, old_dot)
        sitemap_helper(new_page, self.new_processed_pages, new_dot)
        #old_dot.render(f"{self.project_config.project_name}_{self.old_commit}.gv", view=False, format="pdf")
        new_dot.render(f"{self.project_config.project_name}_{self.new_commit}.gv", view=True, format="pdf")







    def get_initial_pages(self):
        return self.db.query(Page, Commit)\
            .join(Commit)\
            .filter(
            Page.commit.has(Project.name == self.project_config.project_name),
            or_(Page.commit.has(Commit.hash == self.old_commit), Page.commit.has(Commit.hash == self.new_commit)),
        )\
            .order_by(Page.added_at)\
            .limit(2)\
            .all()


    def get_next_pages(self, current_page: Page, processed_pages):
        # pages = db.query(Page, Commit) \
        #     .join(Commit) \
        #     .filter(
        #     Page.commit.has(Project.name == self.project_config.project_name),
        #     Page.from_page.any(Page.id == current_page),
        #     or_(Page.commit.has(Commit.hash == old_commit), Page.commit.has(Commit.hash == new_commit)),
        # ) \
        #     .order_by(Page.added_at)\
        #     .all()

        pages = list(filter(lambda x: x.id not in processed_pages, current_page.to_page))

        return pages





    # def get_differences(self, project_name, old_commit, new_commit, page_url):
    #     query = f'''
    #     SELECT
    #     diff.id AS diff_id,
    #     diff.element,
    #     diff.old_screenshot,
    #     diff.new_screenshot,
    #     diff.page_old_id,
    #     diff.page_new_id,
    #     page.id AS page_id,
    #     page.url,
    #     commit.id AS commit_id,
    #     commit.hash,
    #     project.id AS project_id,
    #     project.name AS project_name
    #     FROM
    #     diff
    #     JOIN page ON page.id = diff.page_old_id OR page.id = diff.page_new_id
    #     JOIN commit ON commit.id = page.commit_id
    #     JOIN project ON project.id = commit.project_id
    #
    #
    #     WHERE
    #     project.name = '{project_name}' AND
    #     (commit.hash = '{old_commit}' OR commit.hash = '{new_commit}') AND
    #     page.url = '{page_url}'
    #
    #     ORDER BY diff.id
    #     '''
    #     diffs = db.execute(query)
    #
    #     print(diffs)
    #
    #     db.close()


if __name__ == '__main__':

    p = "ngx-admin"
    c1 = "06d2197583c596215ccc2d539a7e9548f6a3d5ba"
    c2 = "3b63759e8489cdca59d0ed6a6165ed4b7e0bf993"
    u = "http://localhost/"

    result = Result(Config.get_next_project_config(), c1, c2)

    result.get_sitemap()

    #get_differences(p, c1, c2, u)
