# The Sourdough Framework website
This code is responsible to generate the sourdough framework website.

You can preview the website at [https://www.the-sourdough-framework.com](https://www.the-sourdough-framework.com/).

## Installation

Make sure you have ruby installed. The same version as listed in the `.ruby-version` file.

## Building the website

Go to the `../book` folder and run `make website`.

If you want to run the post-processor only, run the processing script with:

```bash
bundle exec ruby modify_build.rb
```

## Viewing the website

Go to the `static_website_html` folder and view the HTML files.
