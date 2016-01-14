use std::net::{TcpListener, TcpStream};
use std::io::{Buffer,}

let listener = TcpListener::bind("localhost:22222").unwrap();

fn handle_client(stream: TcpStream) {
    TcpStream.write_all(
}

fn main() {
    loop {
        for stream in listener.incoming() {
            match stream {
                Ok(stream) => {
                    handle_client(stream)
                }
                Err(e) => { println!("CONNECTION FAILED!!") }
            }
        }
    }
}

