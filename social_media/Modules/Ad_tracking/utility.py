import os

def remove_files_from_directory(directory_path):
    try:
        # List all files in the directory
        files = os.listdir(directory_path)

        # Iterate through each file and remove it
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed file: {file_path}")

        print("All files removed successfully.")

    except Exception as e:
        print(f"Error: {e}")
def save_image_to_binary(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            image_binary = image_file.read()
        return image_binary
    except Exception as e:
        print(f"Error: {e}")

# Convert binary back to image
def convert_binary_to_image(binary_file_path, output_image_path):
    try:
        with open(binary_file_path, 'rb') as binary_file:
            image_binary = binary_file.read()

        with open(output_image_path, 'wb') as image_file:
            image_file.write(image_binary)

        print(f"Binary file converted back to image: {output_image_path}")

    except Exception as e:
        print(f"Error: {e}")