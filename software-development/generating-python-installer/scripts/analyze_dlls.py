"""DLL dependency footprint analyzer for a Nuitka standalone dist folder.

Production strategy reference: 71 DLLs / 93.23 MB total; largest offenders
libopenblas (26.85 MB), opengl32sw (15.25 MB). Stdlib only.

Usage: py analyze_dlls.py <dist-dir>   e.g. py analyze_dlls.py dist/YourApp.dist
"""
import sys
from pathlib import Path


def get_optimization_suggestion(dll_name):
    """Per-family optimization hints based on the DLL name."""
    suggestions = []

    if "openblas" in dll_name or "mkl" in dll_name:
        suggestions.append("Math library; reference build had libopenblas at 26.85 MB")
        suggestions.append("If high-performance compute is not needed, consider a lighter BLAS")
    elif "opencv" in dll_name or "ffmpeg" in dll_name:
        suggestions.append("OpenCV-related; reference build's opencv_videoio_ffmpeg was 18.48 MB")
        suggestions.append("Consider switching to opencv-python-headless")
    elif "qt5" in dll_name or "qt6" in dll_name or "pyside" in dll_name:
        suggestions.append("Qt library; reference build's Qt5Core was 5.13 MB")
        suggestions.append("Exclude unneeded modules (WebEngine, 3D, Charts) at compile time")
    elif "opengl" in dll_name and "sw" in dll_name:
        suggestions.append("OpenGL software renderer; reference kept it at 15.25 MB")
        suggestions.append("Usually safe to delete when hardware rendering is available")
    elif "d3dcompiler" in dll_name:
        suggestions.append("DirectX compiler; reference build had 3.53 MB")
    elif "mfc140" in dll_name:
        suggestions.append("MFC library; reference build had 4.89 MB")

    return suggestions


def analyze_dlls(dist_path):
    """Analyze DLL dependencies inside a dist directory."""
    dist_dir = Path(dist_path)

    if not dist_dir.exists():
        print(f"[ERROR] Directory does not exist: {dist_path}")
        return

    print("=" * 70)
    print("DLL dependency analysis (production strategy)")
    print("=" * 70)

    dll_files = list(dist_dir.rglob("*.dll"))

    if not dll_files:
        print("\nNo DLL files found")
        return

    # Sort by size, largest first
    dll_data = [(dll, dll.stat().st_size) for dll in dll_files]
    dll_data.sort(key=lambda x: x[1], reverse=True)

    total_size = sum(size for _, size in dll_data)

    print(f"\nTotal DLL count: {len(dll_files)}")
    print(f"Total DLL size:  {total_size / 1024 / 1024:.2f} MB\n")

    # Reference comparison
    print("[Reference] Production build DLL profile:")
    print("  - Total count: 71")
    print("  - Total size: 93.23 MB")
    print("  - Largest: libopenblas (26.85 MB), opengl32sw (15.25 MB)\n")

    # Flag DLLs larger than 3MB for attention
    large_dlls = [(dll, size) for dll, size in dll_data if size > 3 * 1024 * 1024]

    if large_dlls:
        print("=" * 70)
        print("WARNING: DLLs larger than 3MB (need attention)")
        print("=" * 70)

        for dll, size in large_dlls:
            size_mb = size / 1024 / 1024
            relative_path = dll.relative_to(dist_dir)

            print(f"\n{size_mb:8.2f} MB  {dll.name}")
            print(f"           location: {relative_path.parent}")

            suggestions = get_optimization_suggestion(dll.name.lower())
            if suggestions:
                for suggestion in suggestions:
                    print(f"            - {suggestion}")

    # Redundancy checks
    print("\n" + "=" * 70)
    print("Redundancy check")
    print("=" * 70)

    # Debug builds (MSVC debug suffix 'd' before .dll, e.g. opengl32swd.dll)
    debug_dlls = [dll for dll, _ in dll_data if dll.stem.endswith('d')]
    if debug_dlls:
        print(f"\nWARNING: Found {len(debug_dlls)} debug-build DLL (deletable):")
        for dll in debug_dlls:
            print(f"  - {dll.name}")
    else:
        print("\nPASS: No debug-build DLLs found (already optimized)")

    # VC++ runtime inventory
    vc_runtimes = [dll for dll, _ in dll_data if 'vcruntime' in dll.name.lower() or 'msvcp' in dll.name.lower()]
    if vc_runtimes:
        print(f"\n[VC++ Runtime] Found {len(vc_runtimes)}:")
        for dll in vc_runtimes:
            size_mb = dll.stat().st_size / 1024 / 1024
            print(f"  - {dll.name} ({size_mb:.2f} MB)")
        print("   These are required; the reference build included them too.")

    # Full DLL list (top 20 by size)
    print("\n" + "=" * 70)
    print("Full DLL list (sorted by size, top 20)")
    print("=" * 70)
    print(f"\n{'Size (MB)':>10}  {'Filename':<34} location")
    print("-" * 70)

    for dll, size in dll_data[:20]:
        size_mb = size / 1024 / 1024
        relative_path = dll.relative_to(dist_dir)
        location = str(relative_path.parent).replace("\\", "/") if relative_path.parent != Path('.') else "(root)"
        print(f"{size_mb:10.2f}  {dll.name:<34} {location}")

    if len(dll_data) > 20:
        remaining_size = sum(size for _, size in dll_data[20:]) / 1024 / 1024
        print(f"... plus {len(dll_data) - 20} more DLLs, {remaining_size:.2f} MB total")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py analyze_dlls.py <dist-dir>")
        print("Example: py analyze_dlls.py dist\\YourApp.dist")
        sys.exit(1)

    analyze_dlls(sys.argv[1])
