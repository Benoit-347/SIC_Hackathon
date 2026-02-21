import argostranslate.package
import argostranslate.translate

def setup_local_translator():
    # 1. Download the language index (happens locally)
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    # 2. Find and install the Spanish-to-English package
    package_to_install = next(
        filter(
            lambda x: x.from_code == 'es' and x.to_code == 'en', available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())
    print("[SYSTEM] Local ES-to-EN model installed successfully.")

def translate_offline(text):
    # No chunking required, no internet required
    return argostranslate.translate.translate(text, 'es', 'en')

# Run setup once, then you can translate massive strings endlessly
# setup_local_translator() 
# result = translate_offline(massive_string)

with open("temp.txt", encoding='UTF-8') as file_1:
    setup_local_translator()
    result = translate_offline(file_1.read())
    
print(f"The output of the translation is: {result}")