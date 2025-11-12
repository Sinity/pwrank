{
  description = "pwRank development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    devenv.url = "github:cachix/devenv";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
    nixpkgs-python.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, devenv, ... } @ inputs:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSystem = nixpkgs.lib.genAttrs systems;
    in {
      packages = forEachSystem (system: {
        devenv-up = self.devShells.${system}.default.config.procfileScript;
      });

      devShells = forEachSystem (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
          };

          # R packages for statistical analysis
          rLibs = with pkgs.rPackages; [
            BradleyTerry2
          ];

          rRuntime = pkgs.rWrapper.override { packages = rLibs; };
        in {
          default = devenv.lib.mkShell {
            inherit inputs pkgs;
            modules = [
              ({ pkgs, config, ... }: {
                # https://devenv.sh/basics/
                devenv.root = builtins.toString ./.;

                # Python backend with uv
                languages.python = {
                  enable = true;
                  version = "3.11";

                  uv = {
                    enable = true;
                    sync = {
                      enable = true;
                      # Sync dev dependencies too
                      allExtras = true;
                    };
                  };
                };

                # JavaScript frontend with bun
                languages.javascript = {
                  enable = true;
                  bun = {
                    enable = true;
                    install.enable = true;
                  };
                  directory = "./frontend";
                };

                # Additional packages
                packages = [
                  rRuntime
                  # Add rpy2 to connect Python with R
                  (pkgs.python311.withPackages (ps: [
                    (ps.rpy2.override { extraRPackages = rLibs; })
                  ]))
                ];

                # Environment variables
                env = {
                  PYTHONPATH = "${config.env.DEVENV_ROOT}/backend:$PYTHONPATH";
                  # R_HOME is set automatically by rWrapper
                };

                # Custom scripts
                scripts = {
                  backend-run = {
                    exec = ''
                      cd backend
                      uv run backend run "$@"
                    '';
                    description = "Run the backend server";
                  };

                  backend-dev = {
                    exec = ''
                      cd backend
                      uv run backend run "$@"
                    '';
                    description = "Run backend in development mode";
                  };

                  frontend-dev = {
                    exec = ''
                      cd frontend
                      bun run serve
                    '';
                    description = "Run the frontend development server";
                  };

                  frontend-build = {
                    exec = ''
                      cd frontend
                      bun run build
                    '';
                    description = "Build frontend for production";
                  };
                };

                # Welcome message
                enterShell = ''
                  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                  echo "  pwRank Development Environment (modernized 2025)"
                  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                  echo ""
                  echo "  Backend (Python + uv):"
                  echo "    backend-run       - Run the backend server"
                  echo "    backend-dev       - Run in development mode"
                  echo "    cd backend && uv  - Use uv directly"
                  echo ""
                  echo "  Frontend (Vue + bun):"
                  echo "    frontend-dev      - Run dev server (Vue hot reload)"
                  echo "    frontend-build    - Build for production"
                  echo "    cd frontend && bun - Use bun directly"
                  echo ""
                  echo "  Tools available:"
                  echo "    - Python ${config.languages.python.version} with uv (100x faster!)"
                  echo "    - Bun (blazingly fast JS runtime)"
                  echo "    - R with BradleyTerry2 for ranking algorithms"
                  echo ""
                  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                '';
              })
            ];
          };
        }
      );
    };
}
