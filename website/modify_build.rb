class ModifyBuild
  def self.build
    new.build
  end

  def build
    build_latex_html
  end

  def build_latex_html
    system("rm -rf #{build_dir}/*")
    system("cd ../book/ && make website")
    system("cp -R ../book/#{build_dir}/* #{build_dir}")
  end

  def list_of_files_to_modify
  end

  private

  def build_dir
    'static_website_html'
  end
end

ModifyBuild.build
