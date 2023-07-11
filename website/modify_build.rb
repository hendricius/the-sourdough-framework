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
    File.open(filename, "w") {|file| file.puts text }
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
end

ModifyBuild.build
