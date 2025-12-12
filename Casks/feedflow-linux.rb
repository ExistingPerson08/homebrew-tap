cask "feedflow-linux" do
  # This cask is for Linux only.
  on_linux do
    version "1.7.0"
    sha256 "28eaca16de18b3ed7522be3c67eb2a6f21a4d4374b1174a4686756fc75b979a6"

    url "https://github.com/prof18/feed-flow/releases/download/#{version}-all/feedflow_#{version}_amd64.deb"
    name "FeedFlow"
    desc "Desktop RSS reader client"
    homepage "https://github.com/prof18/feed-flow/"

    livecheck do
      url :url
      strategy :github_latest do |json|
        tag_match = json["tag_name"]&.match(/^v?(\d+(?:\.\d+)+)-all$/i)
        tag_match&.captures&.first
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

      # OPRAVA 1: Přidáno .to_s k dpkg_executable
      # OPRAVA 2: Opravena neviditelná mezera za `env:`
      system_command dpkg_executable.to_s,
                     args: ["-x", Dir[staged_path/"*.deb"].first, staged_path],
                     env:  { "PATH" => "#{dpkg_bin_path}:#{ENV.fetch("PATH", nil)}" }
    end

    postflight do
      binary_source = staged_path/"opt/feedflow/bin/FeedFlow"
      desktop_file_source = staged_path/"opt/feedflow/lib/feedflow-FeedFlow.desktop"
      icon_source = staged_path/"opt/feedflow/lib/FeedFlow.png"

      odie "Executable not found at '#{binary_source}'. Cask installation failed." unless binary_source.exist?

      binary_target = HOMEBREW_PREFIX/"bin/feedflow"
      FileUtils.ln_sf binary_source, binary_target

      desktop_file_target = Pathname.new(File.expand_path("~/.local/share/applications/feedflow.desktop"))
      text = File.read(desktop_file_source)
      new_contents = text.gsub(/^Exec=.*$/, "Exec=#{binary_target}")
                         .gsub(/^Icon=.*$/, "Icon=feedflow")

      FileUtils.mkdir_p desktop_file_target.dirname
      File.write(desktop_file_target, new_contents)

      icon_target_dir = Pathname.new(File.expand_path("~/.local/share/icons/hicolor/256x256/apps/"))
      FileUtils.mkdir_p icon_target_dir
      FileUtils.cp icon_source, icon_target_dir/"feedflow.png"

      # OPRAVA 3: Přidáno .to_s k argumentu, který je Pathname
      system_command "update-desktop-database", args: ["-q", desktop_file_target.dirname.to_s]
    end

    uninstall_postflight do
      desktop_file_path = Pathname.new(File.expand_path("~/.local/share/applications/feedflow.desktop"))
      icons = Pathname.glob(File.expand_path("~/.local/share/icons/**/feedflow.png"))

      FileUtils.rm(HOMEBREW_PREFIX/"bin/feedflow")
      FileUtils.rm(desktop_file_path)
      FileUtils.rm(icons)

      # OPRAVA 4: Přidáno .to_s k argumentu, který je Pathname
      system_command "update-desktop-database", args: ["-q", desktop_file_path.dirname.to_s]
    end

    zap trash: [
      "~/.cache/FeedFlow",
      "~/.config/FeedFlow",
      "~/.local/share/FeedFlow",
    ]
  end
end
