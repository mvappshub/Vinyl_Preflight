#!/usr/bin/env python3
"""
Pytest testy pro Vinyl Preflight Processor
"""
import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vinyl_preflight_app import PreflightProcessor, _get_wav_duration_worker, safe_round


class TestPreflightProcessor:
    """Testy pro hlavní PreflightProcessor třídu"""
    
    @pytest.fixture
    def processor(self):
        """Vytvoří testovací instanci processoru"""
        def dummy_progress(current, total):
            pass
        def dummy_status(message):
            pass
        return PreflightProcessor(
            api_key="test_key",
            progress_callback=dummy_progress,
            status_callback=dummy_status
        )
    
    @pytest.fixture
    def temp_dir(self):
        """Vytvoří dočasný adresář pro testy"""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path, ignore_errors=True)
    
    def test_empty_directory(self, processor, temp_dir):
        """Test prázdného adresáře"""
        projects = processor._scan_and_group_projects(temp_dir)
        assert projects == {}
    
    def test_directory_with_no_projects(self, processor, temp_dir):
        """Test adresáře bez projektů (bez PDF/WAV)"""
        # Vytvoř adresář s jinými soubory
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        (project_dir / "readme.txt").write_text("test")
        (project_dir / "image.jpg").write_bytes(b"fake image")
        
        projects = processor._scan_and_group_projects(temp_dir)
        assert projects == {}
    
    def test_directory_with_only_pdf(self, processor, temp_dir):
        """Test adresáře s pouze PDF soubory"""
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        (project_dir / "tracklist.pdf").write_bytes(b"%PDF-1.4 fake pdf")
        
        projects = processor._scan_and_group_projects(temp_dir)
        assert projects == {}
    
    def test_directory_with_only_wav(self, processor, temp_dir):
        """Test adresáře s pouze WAV soubory"""
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        (project_dir / "side_a.wav").write_bytes(b"RIFF fake wav")
        
        projects = processor._scan_and_group_projects(temp_dir)
        assert projects == {}
    
    def test_valid_project_structure(self, processor, temp_dir):
        """Test validní struktury projektu"""
        project_dir = temp_dir / "test_project"
        project_dir.mkdir()
        (project_dir / "tracklist.pdf").write_bytes(b"%PDF-1.4 fake pdf")
        (project_dir / "side_a.wav").write_bytes(b"RIFF fake wav")
        
        projects = processor._scan_and_group_projects(temp_dir)
        assert "test_project" in projects
        assert len(projects["test_project"]["pdfs"]) == 1
        assert len(projects["test_project"]["wavs"]) == 1
    
    def test_nonexistent_directory(self, processor):
        """Test neexistujícího adresáře"""
        nonexistent = Path("/nonexistent/directory")
        projects = processor._scan_and_group_projects(nonexistent)
        assert projects == {}


class TestConsolidatedModeDetection:
    """Testy pro detekci consolidated módu"""
    
    @pytest.fixture
    def processor(self):
        def dummy_progress(current, total):
            pass
        def dummy_status(message):
            pass
        return PreflightProcessor(
            api_key="test_key",
            progress_callback=dummy_progress,
            status_callback=dummy_status
        )
    
    def test_empty_wav_list(self, processor):
        """Test prázdného seznamu WAV"""
        from vinyl_preflight.core.validator import detect_consolidated_mode
        assert detect_consolidated_mode([]) == False

    def test_too_many_wavs(self, processor):
        """Test příliš mnoha WAV souborů (>4)"""
        from vinyl_preflight.core.validator import detect_consolidated_mode
        wavs = [f"track_{i:02d}.wav" for i in range(1, 6)]
        assert detect_consolidated_mode(wavs) == False

    def test_individual_tracks(self, processor):
        """Test individual track patterns"""
        from vinyl_preflight.core.validator import detect_consolidated_mode
        wavs = ["01_track.wav", "02_track.wav", "03_track.wav"]
        assert detect_consolidated_mode(wavs) == False

    def test_consolidated_sides(self, processor):
        """Test consolidated side patterns"""
        from vinyl_preflight.core.validator import detect_consolidated_mode
        wavs = ["SIDE A-V2-WAV.wav", "SIDE B-V2-WAV.wav", "SIDE C-V2-WAV.wav"]
        assert detect_consolidated_mode(wavs) == True

    def test_simple_sides(self, processor):
        """Test jednoduchých side patterns"""
        from vinyl_preflight.core.validator import detect_consolidated_mode
        wavs = ["A.wav", "B.wav"]
        assert detect_consolidated_mode(wavs) == True

    def test_mixed_patterns(self, processor):
        """Test smíšených patterns (většina individual)"""
        from vinyl_preflight.core.validator import detect_consolidated_mode
        wavs = ["01_track.wav", "02_track.wav", "side_a.wav"]
        assert detect_consolidated_mode(wavs) == False


class TestWAVProcessing:
    """Testy pro zpracování WAV souborů"""
    
    def test_nonexistent_wav_file(self):
        """Test neexistujícího WAV souboru"""
        nonexistent = Path("/nonexistent/file.wav")
        path_str, duration = _get_wav_duration_worker(nonexistent)
        assert path_str == nonexistent.as_posix()  # Use as_posix() for consistent format
        assert duration is None

    def test_empty_wav_file(self, tmp_path):
        """Test prázdného WAV souboru"""
        empty_wav = tmp_path / "empty.wav"
        empty_wav.write_bytes(b"")

        path_str, duration = _get_wav_duration_worker(empty_wav)
        assert path_str == empty_wav.as_posix()  # Use as_posix() for consistent format
        assert duration is None

    def test_invalid_wav_file(self, tmp_path):
        """Test nevalidního WAV souboru"""
        invalid_wav = tmp_path / "invalid.wav"
        invalid_wav.write_bytes(b"not a wav file")

        path_str, duration = _get_wav_duration_worker(invalid_wav)
        assert path_str == invalid_wav.as_posix()  # Use as_posix() for consistent format
        assert duration is None


class TestUtilityFunctions:
    """Testy pro pomocné funkce"""
    
    def test_safe_round_with_valid_number(self):
        """Test safe_round s validním číslem"""
        assert safe_round(3.14159) == 3.14
        assert safe_round(2.0) == 2.0
        assert safe_round(1.999) == 2.0
    
    def test_safe_round_with_none(self):
        """Test safe_round s None"""
        assert safe_round(None) is None
    
    def test_safe_round_with_different_decimals(self):
        """Test safe_round s různým počtem desetinných míst"""
        assert safe_round(3.14159, 3) == 3.142
        assert safe_round(3.14159, 1) == 3.1
        assert safe_round(3.14159, 0) == 3.0


if __name__ == "__main__":
    pytest.main([__file__])
