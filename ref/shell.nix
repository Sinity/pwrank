let
  pkgs = import <nixpkgs> {};
in
  pkgs.mkShell {
    buildInputs = with pkgs; [
      R
      rPackages.argparser
      rPackages.BradleyTerry2
    ];
  }
