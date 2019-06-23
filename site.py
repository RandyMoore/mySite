from datetime import datetime
from glob import glob
import os
import markdown
import tornado.ioloop
import tornado.locks
import tornado.web
import urllib.parse

POSTS = {}


class EntryModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/entry.html", entry=entry)


class EntryHandler(tornado.web.RequestHandler):
    async def get(self, slug):
        entry = POSTS.get(slug)
        if not entry:
            raise tornado.web.HTTPError(404)
        self.render("modules/entry.html", entry=entry)


class HomeHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("home.html", entries=sorted(POSTS.values(), key=lambda e: e['published'], reverse=True))


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/entry/([^/]+)", EntryHandler),
        ]
        settings = dict(
            blog_title=u"The Blog",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Entry": EntryModule},
        )
        super(Application, self).__init__(handlers, **settings)


async def run_server():
    app = Application()
    app.listen(8888)

    # In this demo the server will simply run until interrupted
    # with Ctrl-C, but if you want to shut down more gracefully,
    # call shutdown_event.set().
    shutdown_event = tornado.locks.Event()
    await shutdown_event.wait()
    

def main():
    entry_path = os.path.join(os.path.dirname(__file__), "blog_entries") + '/'
    for file in glob(entry_path + "*.md"):
        with open(file, "r") as entry_file:
            file_name = file.replace(entry_path, '').replace('.md', '')
            file_name_parts = file_name.split('-')
            title = file_name_parts[-1]
            entry = {
                'slug': file_name,
                'title': title,
                'html': markdown.markdown(entry_file.read()),
                'published': datetime.strptime('-'.join(file_name_parts[:-1]), '%Y-%m-%d')
            }
            POSTS[file_name] = entry
    tornado.ioloop.IOLoop.current().run_sync(run_server)


if __name__ == "__main__":    
    main()
