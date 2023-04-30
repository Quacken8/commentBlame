
import os

commentSymbols = ['//', '#']

ignoredFileExtensions = ['svg', 'png', '.g.dart', 'g.part']
ignoredFileNames = ["makefile", "untranslated.json", "pubspec.lock", "pubspec.yaml"]
ignoredFilePrefixes = ['.', '_']
ignoredDirectories = []
ignoredDirectoryPrefixes = ['.', '_']

def updateWithGitignore(directory):
    try:
        with open(f'{directory}.gitignore') as f:
            for line in f:
                ignoredDirectories.append(line.strip())
                ignoredFileNames.append(line.strip())
    except FileNotFoundError:
        print("No .gitignore file found")

class File:
    comments = []
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.comments = []

    def __str__(self):
        return self.name + " " + self.path

    def __repr__(self):
        return self.name + " " + self.path
    

    def appendComment(self, comment):
        self.comments.append(comment)
    
    def printComments(self):
        if len(self.comments) > 10:
            print("Too many comments to print")
            return
        for comment in self.comments:
            print(comment)

# recursively get all files in directory
import os

def getAllFiles(directory):
    file_paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            if any (ext in filename for ext in ignoredFileExtensions):
                continue
            if filename in ignoredFileNames:
                continue
            if filename[0] in ignoredFilePrefixes:
                continue
            try:
                if root.split('/')[-1] in ignoredDirectories:
                    continue
                if root.split('/')[-1][0] in ignoredDirectoryPrefixes:
                    continue
            except IndexError:
                pass
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    files = []
    for file in file_paths:
        print(file)
        files.append(File(file.split('/')[-1], file))
    return files


def getCommentsFromFile(file):
    with open(file.path) as f:
        try:
            for line in f:
                for symbol in commentSymbols:
                    if symbol in line:
                        splitted = line.split(symbol)
                        file.appendComment(' '.join(splitted[1:]))
                        break
        except UnicodeDecodeError:
            pass

def main():
    directory = ('../cz.ikariera.fairapp/')
    updateWithGitignore(directory)
    files = getAllFiles(directory)
    for file in files:
        getCommentsFromFile(file)

    for file in files:
        if file.comments == []:
            continue
        print("--------------------")
        print(file.name)
        file.printComments()

if __name__ == "__main__":
    main()