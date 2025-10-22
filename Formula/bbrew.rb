class Bbrew < Formula
  desc "A simple TUI tool to make your homebrew bold."
  homepage "https://github.com/Valkyrie00/bold-brew"
  version "2.0.0"

  on_macos do
    if Hardware::CPU.intel?
      url "https://github.com/Valkyrie00/bold-brew/releases/download/v#{version}/bbrew_#{version}_darwin_amd64.tar.gz"
      sha256 "59504099c6815e92fe790fb7c5d87d1fc65b77e3be6f217d8af72e68e9526d81"

      def install
        bin.install "bbrew"
      end
    end
    if Hardware::CPU.arm?
      url "https://github.com/Valkyrie00/bold-brew/releases/download/v#{version}/bbrew_#{version}_darwin_arm64.tar.gz"
      sha256 "98dd8a24ca7efc7019a8056f322c7c3e868d93fb35a39e5235f773853a765f63"

      def install
        bin.install "bbrew"
      end
    end
  end

  on_linux do
    if Hardware::CPU.intel? and Hardware::CPU.is_64_bit?
      url "https://github.com/Valkyrie00/bold-brew/releases/download/v#{version}/bbrew_#{version}_linux_amd64.tar.gz"
      sha256 "a9c1ec72035a11e97e6e4d444be8f5db36196236ed964a66a44ee472a484a81f"
      def install
        bin.install "bbrew"
      end
    end
    if Hardware::CPU.arm? and Hardware::CPU.is_64_bit?
      url "https://github.com/Valkyrie00/bold-brew/releases/download/v#{version}/bbrew_#{version}_linux_arm64.tar.gz"
      sha256 "284143d32290f02649dae97ae73d8ded35ed2c354a9e3c29c081648df508d78f"
      def install
        bin.install "bbrew"
      end
    end
  end

  test do
    system "#{bin}/bbrew --version"
  end
end
