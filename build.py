"""
Simple static site generator

"""
import os
import re
import yaml
import jinja2
import logging
from markdown import render_html

logger = logging.getLogger(__name__)


def slugify(title):
    return title.lower().replace(' ', '-')


class Page(object):
    meta_splitter = re.compile(r'^---(.*?)---?(.*)', re.DOTALL)

    def __init__(self, path):
        self.path = path
        self.text = self.read()
        self.meta = self.get_meta()
        self.html = self.render()

    def get_meta(self):
        match = self.meta_splitter.search(self.text)
        if match:
            yml, text = match.groups()
            self.text = text
            meta = yaml.load(yml)
            meta['slug'] = slugify(meta['title'])
        else:
            meta = {
                'title': 'Untitled',
                'slug': 'untitled',
                'date': '0000-00-00'
            }
        return meta

    def read(self):
        with open(self.path) as text_file:
            return text_file.read()

    def render(self):
        return render_html(self.text)


class Pages(object):
    page_class = Page

    def __init__(self, directory):
        self.directory = directory
        self.pages = self.process_pages()

    def __iter__(self):
        return iter(self.pages)

    def process_pages(self):
        pages = []
        for path in os.listdir(self.directory):
            if path.endswith('.md'):
                page_path = os.path.join(self.directory, path)
                page = self.page_class(page_path)
                pages.append(page)
        return pages


class Jinja2Renderer(object):
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir
        loader = jinja2.FileSystemLoader(templates_dir)
        self.env = jinja2.Environment(loader=loader)

    def render(self, template, data):
        template = self.env.get_template(template)
        return template.render(data)


class Website(object):
    def __init__(self, pages_dir='pages', public_dir='public',
                    templates_dir='templates', renderer=Jinja2Renderer):
        self.pages = Pages(pages_dir)
        self.public_dir = public_dir
        self.templates_dir = templates_dir
        self.renderer = renderer(templates_dir)

    def write_page(self, page):
        logger.debug('page: %s' % page)
        html_path = os.path.join(self.public_dir, page.meta['slug'] + '.html')
        html_content = self.renderer.render('page.html', {'page': page})
        with open(html_path, 'w') as html_file:
            html_file.write(html_content)

    def write_index(self):
        html_content = self.renderer.render('index.html', {'pages': self.pages})
        html_path = os.path.join(self.public_dir, 'index.html')
        with open(html_path, 'w') as index_file:
            index_file.write(html_content)

    def clean_public_dir(self):
        for html_file in os.listdir(self.public_dir):
            if html_file.endswith('.html'):
                os.remove(os.path.join(self.public_dir, html_file))

    def generate(self):
        self.clean_public_dir()
        self.write_index()
        for page in self.pages:
            self.write_page(page)


if __name__ == '__main__':
    site = Website()
    site.generate()
