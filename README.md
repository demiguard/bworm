# bworm

Ever had a bad idea? No worse than that! Like implementing a language in JSON and with build in version control levels of bad idea. Well this library is an attempt to one up, that with levels of WTF were you thinking of.
So for the uninitiated an ORM(Object relational mapping) is a piece of software, that map database constructs into in language constructs or objects in the language. Some people think they are a good idea - because they enforce correctness on queries, and implement protections against SQL injections and encoding errors, that are difficult to think about in advance. Some people think they are a bad idea, because ORM implementations are often limited compared to the full expressive power of SQL, and an ORM internal state might be corrupted in somebody comes around and execute the wrong query.

## The best worst object relational mapping

So lets get started - how do you create a database?

```python
from bworm.sqlite import database
```

Congratulation it was a SQLite database with the filename database.sqlite. If you rather have cookie_dough_recipes.sqlite just:

```python
from bworm.sqlite import cookie_dough_recipes
```

Okay cool, but lets check the tables in the database:

```python
>>>dir(cookie_dough_recipes)
[]
```

Well that's not every surprising - I mean we just created the database - lets add a table

```python
from dataclases import make_dataclass
cookie_dough_recipes.Ingredient = make_dataclass("Ingredient", [("grams", int), ("name", str)]) 
```

## Why is this a terrible idea

This have been left as an exercise for the reader as I ran out of claude tokens. I mean I didn't have any to begin with, but you know.
