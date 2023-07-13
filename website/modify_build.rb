require 'pry'
require 'nokogiri'

# This class goes through the generated default LaTeX HTML and performs
# several optimisations on the HTML. Nokogiri is used to facilitate the
# modifications.

class ModifyBuild
  def self.build
    new.build
  end

  def build
    build_latex_html
  end

  def build_latex_html
    system("rm -rf #{build_dir}/")
    system("mkdir #{build_dir}/")
    copy_source_to_local_dir_for_modification
    list_of_files_to_modify.each do |filename|
      modify_file(filename)
    end
  end

  private

  def modify_file(filename)
    orig_text = File.read(filename)
    text = fix_double_slashes(orig_text)
    text = fix_navigation_bar(text)
    text = fix_titles(text)
    text = fix_menu(text)
    text = fix_cover_page(text) if is_cover_page?(filename)
    File.open(filename, "w") {|file| file.puts text }
  end

  def is_cover_page?(filename)
    ["book.html", "index.html"].any? do |name|
      filename.include?(name)
    end
  end

  def list_of_files_to_modify
    Dir.glob("#{build_dir}/*.html")
  end

  def copy_source_to_local_dir_for_modification
    system("cd ../book/ && make website") unless source_website_output_exists?
    system("cp -R ../book/#{build_dir}/* #{build_dir}")
  end

  def source_website_output_exists?
    File.directory?("../book/#{build_dir}/")
  end

  def build_dir
    'static_website_html'
  end

  def fix_double_slashes(text)
    text.gsub(/\/\//, "/")
  end

  def fix_navigation_bar(text)
    doc = Nokogiri::HTML(text)
    elements = [doc.search('.chapterToc'), doc.search('.sectionToc'), doc.search('.subsectionToc')].flatten
    elements.each do |n|
      chapter_number_or_nothing = n.children[0].text.strip
      hyperlink_node = n.children[1]
      next if hyperlink_node.nil?

      # remove unneeded text and merge into single a tag
      n.children[0].remove
      link_text = hyperlink_node.content
      # no chapter number
      if chapter_number_or_nothing.length == 0
        content = hyperlink_node.to_s
      else
        link_node_content = %Q{
        <span class="chapter_number">#{chapter_number_or_nothing}</span>
        <span class="link_text">#{link_text}</span>
        }
        hyperlink_node.inner_html = link_node_content
        content = hyperlink_node.to_s
      end
      n.inner_html = content
    end
    doc.to_html
  end

  def fix_titles(text)
    doc = Nokogiri::HTML(text)
    title_node = doc.css("title")[0]
    raise ArgumentError.new("No title found in HTML document") if title_node.nil?

    title_node.content = build_title(title_node.content)
    doc.to_html
  end

  # "3 Making a sourdough starter"
  # Should return Making a sourdough starter - The Sourdough Framework"
  def build_title(title)
    # No title, happens on index page in LaTeX build
    return title_appendix if title.length == 0

    # Starts with number
    if title[0].to_i > 0
      use_title = title.split(" ").drop(1).join(" ")
    else
      use_title = title
    end
    "#{use_title} - #{title_appendix}"
  end

  def title_appendix
    "The Sourdough Framework"
  def fix_menu(text)
    doc = Nokogiri::HTML(text)
    nav = doc.css("nav.TOC")[0]
    # page has no nav
    return text unless nav

    menu_items_html = doc.css("nav.TOC > *").to_html
    nav.add_class("menu")
    nav_content = %Q{
      #{menu_mobile_nav}
      <div class="menu-items">#{menu_items_html}</div>
    }
    nav.inner_html = nav_content
    doc.to_html
  end

  def menu_mobile_nav
  %Q{
    <a href="/" class="logo">
      The Sourdough Framework
    </a>
    <input type="checkbox" id="toggle-menu">
    <label class="hamb toggle-menu-label" for="toggle-menu"><span class="hamb-line"></span></label>
  }
  end

  def fix_cover_page(text)
    doc = Nokogiri::HTML(text)
    body = doc.css("body")[0]
    content = doc.css("body > .titlepage")[0]
    menu = doc.css("body > .menu")[0]
    cover = content.css(".center")[0]
    cover_html = cover.to_html
    cover.inner_html = "<a href='Thehistoryofsourdough.html'>#{cover_html}</a>"
    body.inner_html = "#{menu} #{content}"
    doc.to_html
  end
end

ModifyBuild.build
