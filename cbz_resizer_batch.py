import os
import shutil
import sys
import zipfile
from pathlib import Path

import rarfile
from PIL import Image
from send2trash import send2trash


def remove_temp_folder(temp_folder):
    """Rimuove la cartella temporanea."""
    try:
        shutil.rmtree(temp_folder)
    except Exception as e:
        print(
            f"Errore durante la rimozione della cartella temporanea {temp_folder}: {e}"
        )


def get_file_size_mb(file_path):
    """Restituisce la dimensione del file in megabyte."""
    return os.path.getsize(file_path) / (1024 * 1024)


def update_progress_bar(total_images, processed_images):
    """Aggiorna la barra di progresso della compressione delle immagini."""
    progress = processed_images / total_images * 20
    sys.stdout.write("\r")
    sys.stdout.write(
        f"[{'=' * int(progress)}{' ' * (20 - int(progress))}] {processed_images / total_images * 100:.2f}%"
    )
    sys.stdout.flush()


def compress_image(image_path, max_dimension):
    """Comprime un'immagine ridimensionandola in base al fattore specificato."""
    with Image.open(image_path) as image:
        original_width, original_height = image.size
        resize_factor = max_dimension / min(original_width, original_height)

        if resize_factor < 1:
            new_width = int(original_width * resize_factor)
            new_height = int(original_height * resize_factor)
            resized_image = image.resize((new_width, new_height))
            resized_image.save(image_path)
        else:
            new_width = original_width
            new_height = original_height

    return original_width, original_height, new_width, new_height


def extract_comic_book(input_file, temp_folder):
    """Estrae il contenuto di un file CBZ o CBR."""
    if input_file.suffix.lower() == ".cbz":
        with zipfile.ZipFile(input_file, "r") as comic_file:
            comic_file.extractall(temp_folder)
    elif input_file.suffix.lower() == ".cbr":
        with rarfile.RarFile(input_file, "r") as comic_file:
            comic_file.extractall(temp_folder)
    else:
        raise ValueError("Formato file non supportato.")


def compress_comic_book(input_file, output_file, max_dimension):
    """Comprime un file di fumetti (CBZ o CBR) ridimensionando le immagini al suo interno e crea un nuovo CBZ."""
    temp_folder = Path("temp_folder")
    temp_folder.mkdir(exist_ok=True)

    extract_comic_book(input_file, temp_folder)

    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
    images = list(temp_folder.glob("**/*"))
    # Filtra i file che iniziano con '._' e i file che non sono immagini
    images = [
        img
        for img in images
        if img.suffix.lower() in image_extensions and not img.name.startswith("._")
    ]
    total_images = len(images)
    processed_images = 0

    last_original_width = last_original_height = 0
    last_new_width = last_new_height = 0

    for image_path in images:
        original_width, original_height, new_width, new_height = compress_image(
            image_path, max_dimension
        )
        last_original_width, last_original_height = original_width, original_height
        last_new_width, last_new_height = new_width, new_height
        processed_images += 1
        update_progress_bar(total_images, processed_images)

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as new_comic:
        for file in temp_folder.rglob("*"):
            if file.is_file():
                new_comic.write(file, file.relative_to(temp_folder))

    if output_file.exists():
        remove_temp_folder(temp_folder)

    print_size_info(
        input_file,
        output_file,
        last_original_width,
        last_original_height,
        last_new_width,
        last_new_height,
        max_dimension,
    )

    print(f"Removing to trash: {input_file}")
    send2trash(os.path.normpath(input_file))


def print_size_info(
    input_file,
    output_file,
    original_width,
    original_height,
    new_width,
    new_height,
    compression_percentage,
):
    """Stampa le informazioni sulla dimensione originale e compressa del file di fumetti."""
    original_file_size_mb = get_file_size_mb(input_file)
    new_file_size_mb = get_file_size_mb(output_file)
    print("\nRisoluzione".ljust(40) + "Dimensioni".rjust(30))
    print("=" * 70)
    print(
        f"Originale: {original_width}x{original_height}".ljust(40)
        + f"{original_file_size_mb:.2f} MB".rjust(30)
    )
    print(
        f"Nuova: {new_width}x{new_height}".ljust(40)
        + f"{new_file_size_mb:.2f} MB".rjust(30)
    )
    print(f"Percentuale di compressione: {compression_percentage}px".ljust(40))
    print("-" * 70)


def main():
    """Funzione principale che gestisce l'input dell'utente e avvia il processo di compressione."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 comic_resizer.py input_dir [max_dimension]")
        sys.exit(1)

    MAX_DIMENSION = 720
    CBZ = ".cbz"
    RESIZED = ".rsz"

    input_dir = Path(sys.argv[1])

    if len(sys.argv) == 3:
        try:
            MAX_DIMENSION = int(sys.argv[2])
        except ValueError:
            sys.exit(1)

    for input_file in input_dir.rglob(f"*{CBZ}"):
        if len(input_file.suffixes) > 1 and input_file.suffixes[-2] == RESIZED:
            print(f"Skipping: {input_file}")
            continue

        output_file = input_file.with_name(f"{input_file.stem}{RESIZED}{CBZ}")
        print(f"Compressing: {input_file}")
        compress_comic_book(input_file, output_file, MAX_DIMENSION)


if __name__ == "__main__":
    main()
