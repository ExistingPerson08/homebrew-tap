cask "feedflow-linux" do
  # This cask is for Linux only.
  on_linux do
    version "1.5.0"
    sha256 "e57c67e2a0e6cd07cd4d7f2de01df691e309a528435c56990cd444e361c30f77"

    url "https://github.com/prof18/feed-flow/releases/download/#{version}-all/feedflow_#{version}_amd64.deb"
    name "FeedFlow"
    desc "Desktop RSS reader client"
    homepage "https://github.com/prof18/feed-flow/"

    livecheck do
      url :url
      strategy :github_latest do |json|
        json["tag_name"]&.match(/^v?(\d+(?:\.\d+)+)-all$/i)&.captures&.first
      end
    end

    auto_updates true
    depends_on formula: "dpkg"
    depends_on formula: "desktop-file-utils"

    # We handle the extraction manually using `dpkg`.
    container type: :naked

    preflight do
      dpkg_bin_path = Formula["dpkg"].opt_bin
      dpkg_executable = dpkg_bin_path/"dpkg"

      system_command dpkg_executable,
                     args: ["-x", Dir[staged_path/"*.deb"].first, staged_path],
                     env:  { "PATH" => "#{dpkg_bin_path}:#{ENV.fetch("PATH", nil)}" }
    end

    postflight do
      binary_source = staged_path/"opt/feedflow/bin/FeedFlow"
      desktop_file_source = staged_path/"opt/feedflow/lib/feedflow-FeedFlow.desktop"
      icon_source = staged_path/"opt/feedflow/lib/FeedFlow.png"

      unless binary_source.exist?
        odie "Executable not found at '#{binary_source}'. Cask installation failed."
      end

      binary_target = HOMEBREW_PREFIX/"bin/feedflow"
      FileUtils.ln_sf binary_source, binary_target

      desktop_file_target = Pathname.new(File.expand_path("~/.local/share/applications/feedflow.desktop"))
      text = File.read(desktop_file_source)
      new_contents = text.gsub(%r{^Exec=.*$}, "Exec=#{binary_target}")
                         .gsub(%r{^Icon=.*$}, "Icon=feedflow")

      FileUtils.mkdir_p desktop_file_target.dirname
      File.write(desktop_file_target, new_contents)

      icon_target_dir = Pathname.new(File.expand_path("~/.local/share/icons/hicolor/256x256/apps/"))
      FileUtils.mkdir_p icon_target_dir
      FileUtils.cp icon_source, icon_target_dir/"feedflow.png"

      system_command "update-desktop-database", args: ["-q", desktop_file_target.dirname]
    end

    uninstall_postflight do
      desktop_file_path = Pathname.new(File.expand_path("~/.local/share/applications/feedflow.desktop"))
      icons = Pathname.glob(File.expand_path("~/.local/share/icons/**/feedflow.png"))

      FileUtils.rm_f HOMEBREW_PREFIX/"bin/feedflow"
      FileUtils.rm_f desktop_file_path
      FileUtils.rm_f icons

      system_command "update-desktop-database", args: ["-q", desktop_file_path.dirname]
    end

    zap trash: [
      "~/.cache/FeedFlow",
      "~/.config/FeedFlow",
      "~/.local/share/FeedFlow",
    ]
  end
end
