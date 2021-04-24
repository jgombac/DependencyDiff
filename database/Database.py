from sqlalchemy import create_engine, MetaData, Column, Integer, String, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.engine import Engine
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

conn_str = "postgresql://localhost:5432/test_db?user=root&password=root"


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    commits = relationship("Commit", back_populates="project")

    @staticmethod
    def get_or_create(db: Session, name: str):
        project = db.query(Project).filter(Project.name == name).first()
        if not project:
            project = Project(name=name)
            db.add(project)
            db.commit()
        return project

class Commit(Base):
    __tablename__ = "commit"

    id = Column(Integer, primary_key=True)
    hash = Column(String)

    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", back_populates="commits")

    pages = relationship("Page", back_populates="commit")

    @staticmethod
    def get_or_create(db: Session, project_name: str, hash: str):
        project = Project.get_or_create(db, project_name)
        commit = db.query(Commit).filter(Commit.project_id == project.id, Commit.hash == hash).first()
        if not commit:
            commit = Commit(hash=hash, project=project)
            db.add(commit)
            db.commit()
        return commit

class Page(Base):
    __tablename__ = "page"

    id = Column(Integer, primary_key=True)
    url = Column(String)
    visited = Column(Boolean, default=False)
    added_at = Column(TIMESTAMP, default=func.current_timestamp())

    commit_id = Column(Integer, ForeignKey("commit.id"))
    commit = relationship("Commit", back_populates="pages")

    contents = relationship("PageContent", back_populates="page")

    @staticmethod
    def get_or_create(db: Session, project_name: str, commit_hash: str, url: str):
        commit = Commit.get_or_create(db, project_name, commit_hash)
        page = db.query(Page).filter(Page.commit_id == commit.id, Page.url == url).first()
        if not page:
            page = Page(url=url, commit=commit)
            db.add(page)
            db.commit()
        return page

    @staticmethod
    def get_next(db: Session, project_name: str, commit_hash: str, desired_url=None):
        commit = Commit.get_or_create(db, project_name, commit_hash)
        if desired_url:
            return db.query(Page).filter(Page.commit_id == commit.id, Page.visited == False, Page.url == desired_url).order_by(Page.added_at).first()
        return db.query(Page).filter(Page.commit_id == commit.id, Page.visited == False).order_by(Page.added_at).first()



# TODO: only base content atm. Add actions. one page can have multiple contents
class PageContent(Base):
    __tablename__ = "page_content"

    id = Column(Integer, primary_key=True)
    content = Column(String)

    page_id = Column(Integer, ForeignKey("page.id"))
    page = relationship("Page", back_populates="contents")

    @staticmethod
    def get_or_create(db: Session, project_name: str, commit_hash: str, url: str, content: str):
        page = Page.get_or_create(db, project_name, commit_hash, url)
        page_content = db.query(PageContent).filter(PageContent.page_id == page.id).first() # dont query content, it will be present if exists
        if not page_content:
            page_content = PageContent(content=content, page=page)
            db.add(page_content)
            db.commit()
        return page_content


class Diff(Base):
    __tablename__ = "diff"

    id = Column(Integer, primary_key=True)
    element = Column(String)

    page_old_id = Column(Integer, ForeignKey("page.id"))
    page_old = relationship("Page", foreign_keys=[page_old_id])

    page_new_id = Column(Integer, ForeignKey("page.id"))
    page_new = relationship("Page", foreign_keys=[page_new_id])

    @staticmethod
    def get_or_create(db: Session, old_page: int, new_page: int, element: str):
        diff = db.query(Diff)\
            .filter(Diff.page_old_id == old_page, Diff.page_new_id == new_page, Diff.element == element)\
            .first()
        if not diff:
            diff = Diff(element=element, page_old_id=old_page, page_new_id=new_page)
            db.add(diff)
            db.commit()
        return diff


def truncate_db(db: Session):
    # delete all table data (but keep tables)
    # we do cleanup before test 'cause if previous test errored,
    # DB can contain dust
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        db.execute(table.delete())
    db.commit()

def get_engine(echo: bool=False) -> Engine:
    return create_engine(conn_str, echo=echo)

def get_session(echo: bool=False) -> Session:
    return sessionmaker(bind=get_engine(echo))()

def create_database(echo: bool=False):
    Base.metadata.create_all(get_engine(echo))


create_database(True)