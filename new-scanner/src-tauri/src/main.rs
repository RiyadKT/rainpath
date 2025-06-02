#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;
use std::thread;

fn main() {
    // Start the Python backend server in a separate thread
    thread::spawn(|| {
        println!("Starting Python API server...");
        
        #[cfg(target_os = "windows")]
        let python_command = "python";
        
        #[cfg(not(target_os = "windows"))]
        let python_command = "python3";
        
        // Start the Python API server
        let api_path = "../api/app.py";
        println!("Running Python API from: {}", api_path);
        
        let status = Command::new(python_command)
            .arg(api_path)
            .status();
            
        match status {
            Ok(exit_status) => println!("Python server exited with: {}", exit_status),
            Err(e) => eprintln!("Failed to start Python server: {}", e),
        }
    });

    // Build the Tauri application
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}