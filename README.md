# KLS - MCMARR

Implementation of KLS processing pipeline following mcmarr framework. Includes abstract classes of the mcmarr framework.

# Installation

Execute the following command to install the package using pip:

```bash
pip install git+https://github.com/AlbertoCasasOrtiz/kls-mcmarr
```

Backup repository:

```bash
pip install git+https://bitbucket.org/doctorado-sistemas-inteligentes/kls-mcmarr/
```

# Voices

You have to download microsoft windows voices for your language, then select that voice in the code in the response class.

# Internationalization and Localization

Babel and gettext are used for internationalization and localization.

For windows, gettext can be downloaded using [this link](https://docs.djangoproject.com/en/1.8/topics/i18n/translation/#gettext-on-windows). Pybabel can be installed with `pip install Babel`.

Generate .pot template with:

```bash
pybabel extract -F babel.cfg -o .\kls_mcmarr\locales\messages.pot .\kls_mcmarr\
```

Generate .po file with:

```bash
msginit --input=kls_mcmarr/locales/messages.pot --output=kls_mcmarr/locales/en/LC_MESSAGES/messages.po --locale=en_US
```

Or update if already exists with:

```bash
msgmerge --update --backup=none ./kls_mcmarr/locales/en/LC_MESSAGES/messages.po ./kls_mcmarr/locales/messages.pot
```

Compile localization .mo files with:

```bash
msgfmt -o ./kls_mcmarr/locales/en/LC_MESSAGES/messages.mo ./kls_mcmarr/locales/en/LC_MESSAGES/messages.po
```

# Setup instructions for developers

Note: We recommend using [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download/?section=windows) as development environment, since it was the environment used to create the software. The instructions here use Pycharm CE:

 1. Open PyCharm Community Edition and click on **Get from VCS**.
 2. Insert the URL of the repository [https://github.com/AlbertoCasasOrtiz/kls-mcmarr](https://github.com/AlbertoCasasOrtiz/kls-mcmarr) and click **Clone** ().
     - _Note_: If there is a message indicating that **Git is not installed**, click on **download and install**.
     - _Note_: You may need to **login to GitHub**.
 4. Once the repository has been cloned, click on **Trust Project**.
 5. At bottom right, you will see a message **No Interpreter**. Click on it and then in **Add New Interpreter->Add Local Interpreter...**
 6. Configure your interpreter selecting **Python 3.10+** as the base interpreter and click **OK**.
 7. Download the modelf or the affective module from [Google Drive](https://drive.google.com/file/d/18ouyTh0VdmheKkO-T27DOy_W8b7EkrQ8/view?usp=drive_link) and put it inside of `assets/models/affective/` with the name `model.tflite`.
     - Alternativelly it can be placed in `/kls_mcmarr/models/affective/`.
 8. At left, open the file **requirements.txt**.
 9. You will see a notification indicating that some packages have not been installed. Click on **Install Requirements** and install them.
 10. At top you can see a button with the text **Current File**. Click on it and then on **Edit Configurations...**.
 11. Click on **Add new run configuration...** and select **Python tests-->Autodetect**.
 12. Select `kls_mcmarr\test\` as your script path and click **Run**.
 13. If you see the error `from mediapipe.python._framework_bindings import resource_util`, install [Microsoft Visual C++ redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version) and restart your computer.

# Documentation

To generate UML diagrams for classes and packages, use the following command:

```shell
pyreverse -o png -p kls_mcmarr ./kls_mcmarr
```