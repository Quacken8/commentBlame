#!/usr/bin/env python3
import os

commentSymbols = {
    ".py": "#",
    ".java": "//",
    ".cpp": "//",
    ".js": "//",
    ".html": "<!-- -->",
    ".css": "/* */",
    ".php": "// or # or /* */",
    ".rb": "#",
    ".go": "//",
    ".swift": "//",
    ".c": "// or /* */",
    ".h": "// or /* */",
    ".dart": "//",
    ".kt": "//",
    ".scala": "// or /* */",
    ".rs": "//",
    ".sql": "-- or /* */",
    ".pl": "#",
    ".sh": "# or :",
}


def updateWithGitignore(directory, ignoredFileExtensions, ignoredFileNames, ignoredDirectories):
        try:
            with open(f'{directory}.gitignore') as f:
                for line in f:
                    if line[0] == '*':
                        ignoredFileExtensions.append(line.strip()[1:])
                    else:
                        ignoredDirectories.append(line.strip())
                        ignoredFileNames.append(line.strip())
        except FileNotFoundError:
            print("No .gitignore file found")


class File:
    comments = []
    numberOfLines = 0
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
            print(f"Too many comments to print ({len(self.comments)})")
            return
        for comment in self.comments:
            print(comment)

def getCommentsFromFile(filePath: str, commentSymbols):
    """reads file and returns number of lines and number of comments

    Args:
        filePath (str): path to file that is to be scanned
        commentSymbols: list of symbols that are used to mark comments

    Returns:
        file: file object with all the comments
    """

    totalNumberOfLines = 0

    file = File(filePath.split('/')[-1], filePath)

    with open(file.path) as f:
        try:
            for line in f:
                totalNumberOfLines += 1
                # remove strings
                if '"' in line:
                    splitted = line.split('"')
                    line = ' '.join(splitted[0::2])
                if "'" in line:
                    splitted = line.split("'")
                    line = ' '.join(splitted[0::2])
                for symbol in commentSymbols:
                    if symbol in line:
                        splitted = line.split(symbol)
                        file.appendComment(' '.join(splitted[1:]))
                        break
        except UnicodeDecodeError:
            pass
    file.numberOfLines = totalNumberOfLines
    return file

def getAllFiles(directory:str, desiredExtensions, ignoredFileExtensions = [], ignoredFileNames = [], ignoredFilePrefixes = [], ignoredDirectories = [], ignoredDirectoryPrefixes = []):
    """recursively gets all files in directory

    Args:
        directory (str): path to directory that is to be scanned
        desiredExtensions (list): list of file extensions that are to be scanned
        ignoredFileExtensions (list): list of file extensions that are to be ignored
        ignoredFileNames (list): list of file names that are to be ignored
        ignoredFilePrefixes (list): list of file prefixes that are to be ignored
        ignoredDirectories (list): list of directories that are to be ignored
        ignoredDirectoryPrefixes (list): list of directory prefixes that are to be ignored

    Returns:
        list: list of file objects
    """
    
    file_paths = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if not any (ext in filename for ext in desiredExtensions):
                continue
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
        files.append(File(file.split('/')[-1], file))
    return files

def main(directory):

    totalNumberOfLines = 0
    totalNumberOfComments = 0
    ignoredFileExtensions = ["plugin", ".html"]
    ignoredFileNames = ["app_localizations.dart"]
    ignoredFilePrefixes = ['.', '_']
    ignoredDirectories = []
    ignoredDirectoryPrefixes = ['.', '_']

    # recursively get all files in directory
    
    updateWithGitignore(directory, ignoredFileExtensions, ignoredFileNames, ignoredDirectories)
    files = getAllFiles(directory, ".dart", ignoredFileExtensions, ignoredFileNames, ignoredFilePrefixes, ignoredDirectories, ignoredDirectoryPrefixes)
    processedFiles = []
    for file in files:
        try:
            processedFiles.append(getCommentsFromFile(file.path, commentSymbols["."+file.name.split('.')[-1]]))
        except KeyError:
            pass

    for file in processedFiles:
        if file.comments == []:
            continue
        print("--------------------")
        print(file.name)
        file.printComments()
        totalNumberOfLines += file.numberOfLines
        totalNumberOfComments += len(file.comments)

    print (f"Total number of lines: {totalNumberOfLines}")
    print (f"Total number of comments: {totalNumberOfComments}")
    print (f"Percentage of comments: {totalNumberOfComments/totalNumberOfLines*100:.2f} %")

if __name__ == "__main__":
    directory = ('../cz.ikariera.fairapp/')
    main(directory)