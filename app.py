from fasthtml.common import *
from monsterui.all import *
import frontmatter
import pathlib
from fasthtml.components import Uk_theme_switcher
from monsterui.foundations import *

app, rt = fast_app(hdrs=Theme.gray.headers(daisy=True))

def load_book(file_path):
    """Load and parse a book's markdown file"""
    with open(file_path) as f:
        post = frontmatter.load(f)
    return post

def create_mode_picker():
    def _opt(val, txt, **kwargs): return Option(txt, value=val, **kwargs)
    def _optgrp(key, lbl, opts): return Optgroup(data_key=key, label=lbl)(*opts)
    group = _optgrp('mode', '', 
                    [
                        _opt('light','',data_icon='sun'), 
                        _opt('dark','',data_icon='moon')
                    ])
    return Div(Uk_theme_switcher(
                    Select(group, hidden=True, selected=True),  
                    id="mode-picker"
                ), 
               cls="fixed top-4 right-4 z-50 p-2",
                # style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;"
            )

def create_book_page(post):
    """Create the detailed book page using our template"""
    metadata = post.metadata
    return Title(metadata["title"]), Container(
        random_theme_script(),
        DivCentered(
            Card(
                DivCentered(
                    H1(metadata["title"], 
                        cls="text-transparent bg-clip-text bg-gradient-to-r from-primary via-muted to-primary transition-all duration-1000 hover:scale-105",
                        style="font-size: 2.5rem; font-weight: 700; -webkit-text-stroke: 0.5px rgba(0, 0, 0, 0.7);"),
                    H2(metadata["author"], cls=(TextT.muted)),
                    A(
                        Img(
                            src=metadata['cover_img_url'], 
                            cls="rounded-lg hover:scale-105 shadow-lg transition-all duration-1000",
                            style="width:300px"
                        ),
                        cls="rounded-lg overflow-hidden",
                        href=metadata['book_url']
                    ),
                    cls="text-center space-y-6"
                ),
                DivCentered(
                    Section(
                        DivHStacked(
                            Label(f"📅 {metadata['date'].strftime('%B %d, %Y')}", cls=LabelT.secondary),
                            Label(f"📚 {metadata['genre']}", cls=LabelT.secondary),
                            cls="space-x-2"
                        ),
                        cls=SectionT.xs
                    ),
                    cls="mb-6"                            
                ),
                Div(
                    render_md(
                        post.content,
                        class_map={
                            'h3': f'text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary {TextT.xl} {TextT.bold} mb-6 mt-8',
                            'ul': f'{ListT.disc} space-y-4 mb-8',
                            'li': f'{TextT.lg} {TextT.normal} leading-relaxed',
                            'ul ul': f'{ListT.circle} ml-8 mt-4',
                            'ul ul li': f'{TextT.normal} leading-relaxed',
                            'p': f'{TextT.lg} {TextT.normal} mb-4',
                            'img': 'rounded-lg shadow-md hover:shadow-xl transition-shadow duration-200',
                            '*[@class="gallery"]': 'flex flex-row items-center justify-center gap-8'
                        }
                    ),
                    cls = 'space-y-6'
                ),
                cls=CardT.default
            )
        ),
        cls=(ContainerT.lg, 'p-8'),
        style="position: relative; overflow: hidden;"
    )

def create_book_card(metadata, filename):
    """Create a card for the book listing"""
    return A(
        Card(
            DivCentered(
                Img(
                    src=metadata['cover_img_url'],
                    cls="rounded-lg shadow-md hover:scale-105 transition-all duration-300",
                    style="width:200px"
                ),
                H3(metadata['title'],
                   cls="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary"),
                P(metadata['author'], cls=TextT.muted),
                DivHStacked(
                    Label(metadata['genre'], cls=LabelT.secondary),
                    Label(metadata['date'].strftime('%B %d, %Y'), cls=LabelT.secondary),
                    cls="mt-4 space-x-2"
                ),
                cls="space-y-4 p-4"
            ),
            cls=(CardT.hover, "transition-all duration-300 hover:shadow-xl")
        ),
        href=f"/book/{filename}",
    )

def random_theme_script():
    return Script("""
            document.addEventListener('DOMContentLoaded', function() {
                const themes = ['uk-theme-zinc', 'uk-theme-slate', 'uk-theme-red', 
                                'uk-theme-rose', 'uk-theme-orange', 'uk-theme-green', 
                                'uk-theme-blue', 'uk-theme-yellow', 'uk-theme-violet'];
                const randomTheme = themes[Math.floor(Math.random() * themes.length)];
                document.documentElement.className = randomTheme;
            });
        """)

@rt
def index():
    """Homepage with grid of book cards"""
    books_path = pathlib.Path('books')
    book_files = list(books_path.glob('*.md'))
    
    # Create cards for each book
    book_cards = []
    for file in book_files:
        post = load_book(file)
        book_cards.append(create_book_card(post.metadata, file.stem))
    
    return Title("NotesMD"), Container(
        create_mode_picker(),
        random_theme_script(),
        Grid(*book_cards, 
            cols_sm=1, cols_md=2, cols_lg=3, cols_xl=4, 
            gap=6),
        cls=(ContainerT.xl, 'p-8')
    )

@rt("/book/{filename}") 
def get(filename: str):
    """Individual book page"""
    try:
        books_path = pathlib.Path('books')
        book_file = books_path / f"{filename}.md"
        
        if not book_file.exists():
            raise FileNotFoundError
            
        post = load_book(book_file)
        return create_book_page(post)
    except (FileNotFoundError, ValueError) as e:
        return Title("Not Found!"), Container(
            DivCentered(
                H1("Book Not Found", cls=TextT.error),
                P("Sorry, we couldn't find the book you're looking for."),
                A("Return to Library", href="/", cls=ButtonT.primary),
                cls="space-y-6 py-12"
            )
        )

serve()
