import uosc.client

class OSCClient:
    """Wrapper for OSC client functionality"""
    
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client = uosc.client.Client(server_ip, server_port)
    
    def fire_clip(self, track_id, clip_id=0):
        """Send OSC message to fire clip"""
        try:
            self.client.send('/live/clip/fire', track_id, clip_id)
            print(f"Sent OSC: /live/clip/fire {track_id} {clip_id}")
        except Exception as e:
            print(f"Error sending OSC message: {e}")
    
    def stop_track(self, track_id):
        """Send OSC message to stop all clips on track"""
        try:
            self.client.send('/live/track/stop_all_clips', track_id)
        except Exception as e:
            pass
    
    def stop_tracks(self, track_ids):
        """Stop all clips on multiple tracks"""
        for track_id in track_ids:
            self.stop_track(track_id)
    
    def close(self):
        """Close OSC client connection"""
        try:
            self.client.close()
        except Exception as e:
            print(f"Error closing OSC client: {e}")
