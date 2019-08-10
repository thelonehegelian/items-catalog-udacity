from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Book, Base, User

engine = create_engine('sqlite:///bookstore.db')

# Clear database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# dummy user
User1 = User(
    name="Umair",
    email="umair@udacity.com",
    picture=('https://pbs.twimg.com/profile_images/'
             '2671170543/18debd694829ed78203a5a36dd364160_400x400.png'))
session.add(User1)
session.commit()

# Category 1
category1 = Category(name="Philosophy")
session.add(category1)
session.commit()

# Book 1
book1 = Book(name="Politics by Aristotle",
             description="Politics is a work of political philosophy"
             "by Aristotle, a 4th-century BC Greek philosopher.",
             category=category1)
session.add(book1)
session.commit()

# Book 2
book2 = Book(name="Utilitarianism by John Stuart Mill",
             description="John Stuart Mills book Utilitarianism "
             "is a classic exposition and defence of "
             "utilitarianism in ethics. The essay first appeared as"
             "a series of three articles published "
             "in Frasers Magazine in 1861. The articles were collected and "
             "reprinted as a single book in 1863.", category=category1)
session.add(book2)
session.commit()

# Category 2
category2 = Category(name="History")
session.add(category2)
session.commit()

# Book 1
book1 = Book(name="A Study of History by Arnold Toynbee",
             description="A Study of History is a 12 volume universal "
             "history by the British historian Arnold J. Toynbee.",
             category=category2)
session.add(book1)
session.commit()

# Book 2
book2 = Book(name="The City by Lewis Mumford",
             description="The development of the city from ancient times to
             "the modern age. Winner of the National Book Award. "
             "One of the major works of scholarship of the twentieth"
             "century", category=category2)
session.add(book2)
session.commit()

# Category 3
category3 = Category(name="Psychology")
session.add(category3)
session.commit()

# Book 1
book1 = Book(name="The Principles of Psychology by William James",
             description="The Principles of Psychology is an 1890 book about "
             "psychology by William James, an American philosopher "
             "and psychologist who trained to be a physician before "
             "going into psychology.", category=category3)
session.add(book1)
session.commit()

# Book 2
book2 = Book(name="The Interpretation of Dreams",
             description="The Interpretation of Dreams "
             "(German: Die Traumdeutung) is an 1899 book by Sigmund Freud"
             "the founder of psychoanalysis,"
             "in which the author introduces his theory of the"
             "unconscious with respect to dream interpretation,"
             "and discusses what would later become the theory of the "
             "Oedipus complex. Freud revised the book at least"
             "eight times and, in the third edition, added an"
             "extensive section which treated dream symbolism "
             "very literally, following the influence of Wilhelm Stekel. "
             "Freud said of this work, Insight such as this falls "
             "to one's lot but once in a lifetime. Dated 1900, "
             "the book was first published in an edition of 600 copies, "
             "which did not sell out for eight years. "
             "The Interpretation of Dreams later gained in popularity,"
             "and seven more editions were published in "
             "Freud's lifetime. Because of the books length and complexity, "
             "Freud also wrote an abridged version called On Dreams. "
             "The original text is widely regarded as one of "
             "Freud's most significant works. ",
             category=category3)
session.add(book2)
session.commit()


print "Books added"
