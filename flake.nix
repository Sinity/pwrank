{
  description = "pwRank development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    devshell.url = "github:numtide/devshell";
  };

  outputs = { self, nixpkgs, flake-utils, devshell }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [
          devshell.overlays.default
        ];

        pkgs = import nixpkgs {
          inherit system overlays;
          config.allowUnfree = true;
        };

        rLibs = with pkgs.rPackages; [
          BradleyTerry2
        ];

        rRuntime = pkgs.rWrapper.override { packages = rLibs; };
        pythonRpy2 = pkgs.python311Packages.rpy2.override { extraRPackages = rLibs; };

        nodeGlobal = import ./frontend/npm_global/default.nix {
          inherit pkgs system;
          nodejs = pkgs.nodejs_20;
        };

      in {
        devShells.default = pkgs.devshell.mkShell {
          devshell = {
            name = "pwRank";
            motd = ''
              pwRank dev shell
              ----------------
              Commands:
                backend:run   poetry run backend run
                frontend:dev  cd frontend && npm run serve

              Enter with `nix develop`.
            '';
          };

          packages = [
            pkgs.poetry
            pkgs.python311
            rRuntime
            pythonRpy2
            pkgs.nodejs_20
            pkgs.nodePackages.node2nix
            nodeGlobal."@vue/cli"
            nodeGlobal.vls
          ];

          env = [
            {
              name = "POETRY_VIRTUALENVS_IN_PROJECT";
              value = "true";
            }
          ];

          commands = [
            {
              name = "backend:run";
              category = "development";
              command = "poetry run backend run";
            }
            {
              name = "frontend:dev";
              category = "development";
              command = "cd frontend && npm run serve";
            }
          ];
        };
      });
}
