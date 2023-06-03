{ pkgs }: {
    deps = [
        pkgs.texlive.combined.scheme-full
			  pkgs.httplz
				pkgs.texlab
        pkgs.biber
    ];
}