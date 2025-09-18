class BetterPkg < Formula
  desc "Universal package manager wrapper"
  homepage "https://github.com/ExistingPerson08/Better-pkg"
  url "https://github.com/ExistingPerson08/Better-pkg/archive/refs/tags/1.1.1.tar.gz"
  sha256 "6f5864b02d5b13ad6ee3abf23237b831a7d42fc0e09e59a1cb5e893f65762055"
  license "GPL-3.0-or-later"
  head "https://github.com/ExistingPerson08/Better-pkg.git", branch: "main"

  depends_on "python@3.12"

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
end
