from app.services.detector import ConfigChangeDetector
from app.services.monitor import MonitorService

def test_detect_configuration_change(): assert ConfigChangeDetector().detect('User admin executed the command configure terminal').detected
def test_ignore_normal_log(): assert not ConfigChangeDetector().detect('Interface GigabitEthernet0/1 is up').detected

def test_duplicate_event():
    event = {'timestamp': '2026-08-14T08:15:32Z', 'source': '192.168.1.1', 'message': 'User admin executed the command'}
    assert MonitorService.fingerprint_for(event) == MonitorService.fingerprint_for(event)
