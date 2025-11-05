#!/bin/bash
# Vercel Build Script
echo "Starting Hugo build with version $HUGO_VERSION"
hugo --gc --minify
echo "Build completed successfully"


