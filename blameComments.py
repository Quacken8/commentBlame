#!/usr/bin/env python3
import os
from symbols import *


def updateWithGitignore(
    directory, ignoredFileExtensions, ignoredFileNames, ignoredDirectories
):
    try:
        with open(f"{directory}.gitignore") as f:
            for line in f:
                if line[0] == "*":
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


def getCommentsFromFile(filePath: str):
    """reads file and returns number of lines and number of comments

    Args:
        filePath (str): path to file that is to be scanned

    Returns:
        file: file object with all the comments
    """

    totalNumberOfLines = 0

    file = File(filePath.split("/")[-1], filePath)

    with open(file.path) as f:
        relevantCommentSymbols = ()
        openingCommentSymbol = None
        closingCommentSymbol = None
        fileExtension = "." + file.name.split(".")[-1]
        try:
            relevantCommentSymbols = commentSymbols[fileExtension]
        except KeyError:
            return file
        try:  # not every file extension has paired comment symbols
            openingCommentSymbol, closingCommentSymbol = pairedCommentSymbols[
                fileExtension
            ]
        except KeyError:
            pass
        try:
            commentEnd = None
            for line in f:
                totalNumberOfLines += 1
                # if comment is not finished look for end of comment
                if commentEnd is not None:
                    if commentEnd in line:
                        file.appendComment(line.split(commentEnd)[0])
                        commentEnd = None
                    else:
                        file.appendComment(line)
                    continue
                # remove strings
                if '"' in line:
                    splitted = line.split('"')
                    line = " ".join(splitted[0::2])
                if "'" in line:
                    splitted = line.split("'")
                    line = " ".join(splitted[0::2])
                # find comments
                # make sure that you only take into account the first comment symbol
                # if there are multiple comment symbols in one line the behaviour is different
                # depending on whether the first one is a paired comment symbol or not
                if openingCommentSymbol is not None and openingCommentSymbol in line:
                    # first check whether normal comment symbol isn't first
                    for commentSymbol in relevantCommentSymbols:
                        if commentSymbol in line.split(openingCommentSymbol)[0]:
                            # found normal comment symbol earlier, don't care
                            continue
                    # ok, there is opening comment symbol, is there also closing comment symbol?
                    if closingCommentSymbol in line.split(openingCommentSymbol)[-1]:
                        file.appendComment(
                            line.split(openingCommentSymbol)[-1].split(
                                closingCommentSymbol
                            )[0]
                        )
                    else:
                        file.appendComment(line.split(openingCommentSymbol)[-1])
                        commentEnd = closingCommentSymbol
                # now that pair comments are done, look for normal comments
                for commentSymbol in relevantCommentSymbols:
                    if commentSymbol in line:
                        file.appendComment(line.split(commentSymbol)[1])
                        break

        except UnicodeDecodeError:
            pass
    file.numberOfLines = totalNumberOfLines
    return file


def getAllFiles(
    directory: str,
    desiredExtensions,
    ignoredFileExtensions=[],
    ignoredFileNames=[],
    ignoredFilePrefixes=[],
    ignoredDirectories=[],
    ignoredDirectoryPrefixes=[],
):
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
            if not any(ext in filename for ext in desiredExtensions):
                continue
            if any(ext in filename for ext in ignoredFileExtensions):
                continue
            if filename in ignoredFileNames:
                continue
            if filename[0] in ignoredFilePrefixes:
                continue
            try:
                if root.split("/")[-1] in ignoredDirectories:
                    continue
                if root.split("/")[-1][0] in ignoredDirectoryPrefixes:
                    continue
            except IndexError:
                pass
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    files = []
    for file in file_paths:
        files.append(File(file.split("/")[-1], file))
    return files


def main(directory):
    totalNumberOfLines = 0
    totalNumberOfComments = 0
    ignoredFileExtensions = ["plugin", ".g.dart"]
    ignoredFileNames = ["app_localizations.dart"]
    ignoredFilePrefixes = [".", "_"]
    ignoredDirectories = []
    ignoredDirectoryPrefixes = [".", "_"]

    # recursively get all files in directory

    updateWithGitignore(
        directory, ignoredFileExtensions, ignoredFileNames, ignoredDirectories
    )
    files = getAllFiles(
        directory,
        ".dart",
        ignoredFileExtensions,
        ignoredFileNames,
        ignoredFilePrefixes,
        ignoredDirectories,
        ignoredDirectoryPrefixes,
    )
    processedFiles = []
    for file in files:
        try:
            processedFiles.append(getCommentsFromFile(file.path))
        except KeyError:
            pass

    for file in processedFiles:
        totalNumberOfLines += file.numberOfLines
        totalNumberOfComments += len(file.comments)

    print(f"Total number of lines: {totalNumberOfLines}")
    print(f"Total number of comments: {totalNumberOfComments}")
    print(
        f"Percentage of comments: {totalNumberOfComments/totalNumberOfLines*100:.2f} %"
    )


if __name__ == "__main__":
    directory = "../cz.ikariera.fairapp/"
    main(directory)
