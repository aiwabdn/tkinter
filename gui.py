import pprint
from glob import glob
from tkinter import *
from PIL import Image, ImageTk
from threadgenius import ThreadGenius
from threadgenius.types import ImageFileInput, ImageUrlInput
import urllib, cStringIO
import webbrowser as wb

class GUI:
    # initialise UI with root element and path of folder of images
    def __init__(self, root, img_path):
        self.threshold = 0.3
        # ThreadGenius api key
        api_key = 'key_MmQxM2Y5M2Q0MDg0MmY2MTc1MjVlYWJmYmYyZDVh'
        self.tg = ThreadGenius(api_key=api_key)
        self.pp = pprint.PrettyPrinter(indent=2, depth=10)
        self.pp = self.pp.pprint
        self.img_path = img_path
        self.img_list = glob(img_path+'/*')
        self.current_img_idx = 0
        self.root = root
        self.root.title("A simple GUI")
        self.build_elements()

    def convert_image(self, img_path):
        # convert image to PhotoImage format and resize to fit into element
        img = Image.open(img_path)
        img = img.resize((300, 300), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        return img

    def build_elements(self):
        # declare all UI elements here. Each element falls under one root.
        img = self.convert_image(self.img_list[self.current_img_idx])
        self.original = Label(self.root, image=img)
        self.original.image = img
        self.next = Button(self.root, text='next', command=self.next_img)
        self.previous = Button(self.root, text='previous', command=self.prev_img)
        self.tag = Button(self.root, text='tag', command=self.get_tags)
        self.ss = Button(self.root, text='shop style', command=self.get_ss)
        self.bl = Button(self.root, text='blog lovin', command=self.get_bl)
        # output is set to a scrollable text widget. All kinds of elements can be pasted to text widget
        self.output = Text(self.root, width=50)
        self.scroll = Scrollbar(self.root, orient=VERTICAL, command=self.output.yview)
        self.output.configure(yscrollcommand=self.scroll.set)
        self.quit = Button(self.root, text='QUIT', command=self.root.quit)
        self.set_grid()

    def set_grid(self):
        # set UI elements to grid
        self.original.grid(row=0, column=0, rowspan=6, padx=5, pady=5)
        self.next.grid(row=0, column=1)
        self.previous.grid(row=1, column=1)
        self.tag.grid(row=2, column=1)
        self.ss.grid(row=3, column=1)
        self.bl.grid(row=4, column=1)
        self.output.grid(row=0, column=2, sticky=N+E+W+S, rowspan=6, padx=5, pady=5)
        self.scroll.grid(row=0, column=3, sticky=N+S)
        self.quit.grid(row=6, column=1, sticky=N+E+W+S)

    # following methods are specific to the ThreadGenius use case. Replace with case specific actions for buttons
    def get_ss(self):
        # get closest matches from ShopStyle catalog
        image = ImageFileInput(file_object=open(self.img_list[self.current_img_idx], 'rb'))
        resp = self.tg.search_by_image(
                catalog_gid='shopstyle',
                image=image,
                n_results=5)
        cat = [(_['object']['metadata'], _['score']) for _ in resp['response']['results'] if _['score']>self.threshold]
        self.output.insert(END, '\n   SHOP STYLE matches  \n')
        if len(cat)>0:
            self.output.images = {}
            for i, (x,_) in enumerate(cat):
                img = Image.open(cStringIO.StringIO(urllib.urlopen(x['thumbnailUrl']).read()))
                img = img.resize((100, 100), Image.ANTIALIAS)
                img = ImageTk.PhotoImage(img)
                self.output.images[i] = img
                self.output.image_create(END, image=img)

    def get_bl(self):
        # get closest matches from BlogLovin catalog
        image = ImageFileInput(file_object=open(self.img_list[self.current_img_idx], 'rb'))
        resp = self.tg.search_by_image(
                catalog_gid='bloglovin_fashion',
                image=image,
                n_results=5)
        cat = [(_['object']['metadata'], _['score']) for _ in resp['response']['results'] if _['score']>self.threshold]
        self.output.insert(END, '\n   BLOGLOVIN  matches  \n')
        if len(cat)>0:
            for x,_ in cat:
                link = Label(self.output, text=x['title'], fg='blue', cursor='hand2')
                self.output.window_create(END, window=link)
                link.bind('<Button-1>', self.callback(x['extUrl']))
                self.output.insert(END, '\n')

    def callback(self, url):
        # method to open clicked url in browser
        wb.open_new(url)

    def get_tags(self):
        # get description tags from TG predictions api
        image = ImageFileInput(file_object=open(self.img_list[self.current_img_idx], 'rb'))
        resp = self.tg.tag_image(image)
        out = [(_['type'], _['name'], _['confidence']) for _ in resp['response']['prediction']['data']['tags'] if _['confidence']>self.threshold]
        if len(out)>0:
            fmt = '{:<8}{:<15}{:<10}'
            self.output.insert(END, '\n   TAGS predicted  \n')
            self.output.insert(END, fmt.format('type', 'name', 'confidence') + '\n')
            for x,y,z in out:
                self.output.insert(END, fmt.format(x,y,z) + '\n')

    def prev_img(self):
        # move to previous image in list
        if self.current_img_idx==0:
            return
        self.current_img_idx -= 1
        img = self.convert_image(self.img_list[self.current_img_idx])
        self.original.configure(image=img)
        self.original.image = img
        self.output.delete(1.0, END)

    def next_img(self):
        if self.current_img_idx == len(self.img_list) - 1:
            return
        self.current_img_idx += 1
        img = self.convert_image(self.img_list[self.current_img_idx])
        self.original.configure(image=img)
        self.original.image = img
        self.output.delete(1.0, END)
