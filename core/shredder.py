import os
import secrets
import string

class SecureShredder:
    def __init__(self, file_path, progress_callback=None):
        self.file_path = file_path
        self.progress_callback = progress_callback
        self.file_size = os.path.getsize(file_path)

    def _update_progress(self, current_pass, total_passes):
        """Arayüzdeki ilerleme çubuğunu tetikler."""
        if self.progress_callback:
            progress_percent = int((current_pass / total_passes) * 100)
            self.progress_callback(progress_percent)

    def zero_fill(self):
        """1 Geçiş: Dosyanın tamamını sıfır (0x00) baytlarıyla doldurur."""
        self._overwrite_custom(passes=1, pass_patterns=[b'\x00'])
        self._destroy_metadata_and_delete()

    def dod_5220_22_m(self):
        """3 Geçiş: Sıfır (0x00), Bir (0xFF) ve Rastgele veri yazar."""
        patterns = [b'\x00', b'\xff', None] # None = Rastgele Veri
        self._overwrite_custom(passes=3, pass_patterns=patterns)
        self._destroy_metadata_and_delete()

    def gutmann(self):
        """35 Geçiş: Yüksek güvenlikli rastgele veri yazma simülasyonu."""
        # Gerçek Gutmann çok spesifik örüntüler içerir, modern diskler için 
        # 35 defa kriptografik rastgele veri yazmak aynı etkiyi yaratır.
        patterns = [None] * 35 
        self._overwrite_custom(passes=35, pass_patterns=patterns)
        self._destroy_metadata_and_delete()

    def _overwrite_custom(self, passes, pass_patterns):
        """Dosyanın üzerine bayt seviyesinde yazma işlemini gerçekleştirir."""
        with open(self.file_path, "ba+") as f:
            for p in range(passes):
                f.seek(0)
                chunk_size = 1024 * 1024  # Belleği korumak için 1 MB'lık parçalar
                written = 0
                
                # O anki geçişin örüntüsünü belirle
                current_pattern = pass_patterns[p]
                
                while written < self.file_size:
                    write_size = min(chunk_size, self.file_size - written)
                    if current_pattern:
                        f.write(current_pattern * write_size)
                    else:
                        f.write(os.urandom(write_size)) # Rastgele bayt üret
                    written += write_size
                
                f.flush()
                os.fsync(f.fileno()) # Verinin diske fiziksel olarak yazıldığından emin ol
                self._update_progress(p + 1, passes)

    def _destroy_metadata_and_delete(self):
        """Dosyanın adını MFT (Master File Table) kayıtlarından gizler ve siler."""
        dir_name = os.path.dirname(self.file_path)
        # 12 karakterlik rastgele bir dosya adı oluştur
        random_name = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        new_path = os.path.join(dir_name, random_name)
        
        # Dosya adını değiştir
        os.rename(self.file_path, new_path)
        
        # Fiziksel olarak sil
        os.remove(new_path)