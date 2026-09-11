{
  description = "SIGHTS Development Environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          python3
          uv
          nodejs
          corepack
          tmux
          stdenv.cc.cc.lib
          libGL
          glib
          zlib
          ruff
        ];

        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.libGL
            pkgs.glib
            pkgs.zlib
          ]}:$LD_LIBRARY_PATH"

          echo == Python Deps ==
          cd server
          uv sync
          echo == JS Deps ==
          cd ../
          yarn
        '';
      };
    };
}

# ttyd -p 8001 ssh localhost
