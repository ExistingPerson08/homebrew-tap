class BetterPkg < Formula
  desc "Universal package manager wrapper"
  homepage "https://github.com/ExistingPerson08/Better-pkg"
  url "https://github.com/ExistingPerson08/Better-pkg/archive/refs/tags/1.1.1.tar.gz"
  sha256 "6f5864b02d5b13ad6ee3abf23237b831a7d42fc0e09e59a1cb5e893f65762055"
  license "GPL-3.0-or-later"
  head "https://github.com/ExistingPerson08/Better-pkg.git", branch: "main"

  depends_on "python@3.12"

  resource "requests" do
    url "https://files.pythonhosted.org/packages/c9/74/b3ff8e6c8446842c3f5c837e9c3dfcfe2018ea6ecef224c710c85ef728f4/requests-2.32.5.tar.gz"
    sha256 "dbba0bac56e100853db0ea71b82b4dfd5fe2bf6d3754a8893c3af500cec7d7cf"
  end
  
  def install
    bin.install "better-pkg"
    pkgshare.install Dir["*"]
  end

  def zap
    rm_r [
      "~/.config/better-tools",
      "~/.local/share/better-tools",
      "~/.local/share/better-tools/plugins",
      "~/.cache/better-tools",
    ]
  end

  test do
    assert_match "better-pkg", shell_output("#{bin}/better-pkg --help")
  end
end
