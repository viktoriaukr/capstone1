# Book Lover

## Overview

"Book Lover" is a web-based book search and interaction application. It allows users to browse books by title or author, leave comments, add ratings, share personal opinions, and manage their reading lists.

## Features

- Book Search: Search for books by title or author.
- Comment Section: Leave comments on books, with ownership control.
- Ratings: Add ratings to express your assessment of books.
- Personal Opinions: Share your thoughts and reviews about books.
- User Authentication: Create and manage user accounts.
- Book Lists: Organize books into "Read," "Currently Reading," or "Want to Read" lists.

### Technology Stack

* Back End
    * Python
    * Flask
    * SQLAlchemy ORM with PostgreSQL database
    * WTForms
    * bcrypt for password security
* Front End
    * Jinja2 HTML Templates
    * Bootstrap styling with custom SCSS
 
### Follow-up Goals
* Styling form for submitting comment/review and rating.
* Adding ability to update "status" on books in "My Books" list.
* Adding loading page.
* Creating "Quiz" feature. (It would help users to discover new books based on a quiz results).

#### The site makes use of the [Open Library API](https://openlibrary.org/developers/api) to retrieve information about books and authors. The Open Library API provides a rich source of book-related data, including book details, author information, and more. This data enhances the content and functionality of "Book Lover."
