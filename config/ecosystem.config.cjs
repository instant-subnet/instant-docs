const path = require("path");

const projectRoot = path.resolve(__dirname, "..");

module.exports = {
  apps: [
    {
      name: "instant-docs-updater",
      script: path.join(projectRoot, "scripts", "start_docs.py"),
      interpreter: "/usr/bin/python3",
      cwd: projectRoot,
      autorestart: true,
      restart_delay: 30000,
      max_restarts: 100,
    },
  ],
};
