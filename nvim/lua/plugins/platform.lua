return {
  {
    "saghen/blink.cmp",
    opts = {
      fuzzy = {
        -- Fedora uses glibc; the portable Neovim binary can be detected as musl.
        prebuilt_binaries = { force_system_triple = "x86_64-unknown-linux-gnu" },
      },
    },
  },
}
