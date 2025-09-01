# Claude Code Context

## Environment Information
- **Platform**: Raspberry Pi
- **OS**: Linux 6.12.25+rpt-rpi-v8 (ARM-based)
- **Architecture**: ARM (likely ARMv8/64-bit based on kernel version)

## Important Notes

### NPM and Node.js on Raspberry Pi
- The Raspberry Pi ARM architecture may have compatibility issues with some npm packages
- Some packages may not have pre-built ARM binaries and need to compile from source
- Installation times can be significantly longer on Raspberry Pi due to limited CPU resources
- Use longer timeouts for npm operations (5-10 minutes recommended)

### Common Issues and Solutions

#### Module Installation Issues
- If npm modules fail to install or have missing files, try:
  1. Clear npm cache: `npm cache clean --force`
  2. Remove node_modules and package-lock.json: `rm -rf node_modules package-lock.json`
  3. Reinstall with longer timeout: `npm install --loglevel=error`
  4. For persistent issues, try using `--force` flag: `npm install --force`

#### Locale Warning
- The system shows locale warnings: `LC_ALL: cannot change locale (en_US.UTF-8)`
- This is a non-critical warning on Raspberry Pi and can be ignored
- To fix permanently, the user can run: `sudo raspi-config` and configure locales

### Development Commands
- **Frontend development**: `npm run dev:frontend` (runs from root, changes to frontend dir)
- **Backend development**: `npm run dev:backend`
- **Full stack development**: `npm run dev`
- **Build frontend**: `npm run build`

### Project Structure
```
training_monitor/
├── frontend/          # React frontend application
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   └── package.json
├── backend/          # Node.js backend server
├── package.json      # Root package.json with dev scripts
└── CLAUDE.md        # This file
```

### Performance Considerations
- Raspberry Pi has limited resources compared to typical development machines
- Build processes may take significantly longer
- Consider using production builds for better performance
- Monitor memory usage during development as Raspberry Pi may have limited RAM

### Testing on Raspberry Pi
- Some testing frameworks may have ARM compatibility issues
- Browser automation tools (like Puppeteer) may require additional ARM-specific setup
- Consider running tests in headless mode to save resources