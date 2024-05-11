{
  description = "Temp";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs = {
        flake-utils.follows = "utils";
        nixpkgs.follows = "nixpkgs";
      };
    };
  };


  outputs = inputs @ {
    self,
    nixpkgs,
    utils,
    ...
  }:
  # eachDefaultSystem is effectively a copy and paste of the same config multiple times,
  # with the main difference being the system, which for our purposes includes x86 and arm64 linux.
  # should allow for users of nix on macos to build there, but I'm not testing it.
    utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix {inherit pkgs;};
      temp123456 = self.packages.${system}.temp1234;
      cmd = "${temp123456}/bin/";
      overrides = poetry2nix.overrides.withDefaults (final: prev: {});
      python_version = pkgs.python312;
    in {
      packages = {
        # dockerImage = pkgs.dockerTools.buildImage {
        #   name = "sync";
        #   tag = "latest";
        #   config = {
        #     Cmd = [cmd];
        #   };
        # };

        # defines the poetry application that we want to build
        # reads in pyproject.toml and poetry.lock to do this
        temp1234 = poetry2nix.mkPoetryApplication {
          projectDir = ./.;
          overrides = overrides;
          python = python_version;
        };

        # a nix idiom where default has a special meaning, so if you run
        # nix build . then this is what will get built
        default = temp123456;
      };

      devShells.default = let
        env = poetry2nix.mkPoetryEnv {
          projectDir = ./.;
          overrides = overrides;
          python = python_version;
        };
      in
        env.env.overrideAttrs (old: {
          nativeBuildInputs =
            (old.nativeBuildInputs or [])
            ++ [
              # add extra packages you want available in the dev env
              pkgs.poetry
            ];
        });
    });
}