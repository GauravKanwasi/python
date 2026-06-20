import tkinter as tk
from tkinter import ttk, messagebox
import threading

class PerfectNumberChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Perfect Number Checker")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Set style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Perfect Number Checker", 
                         font=('Helvetica', 18, 'bold'))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Description
        desc = ttk.Label(main_frame, 
                        text="A perfect number equals the sum of its proper divisors\nExample: 6 = 1 + 2 + 3",
                        justify=tk.CENTER, font=('Helvetica', 10))
        desc.grid(row=1, column=0, columnspan=3, pady=5)
        
        # Single number check section
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(main_frame, text="Check Single Number", 
                 font=('Helvetica', 12, 'bold')).grid(row=3, column=0, columnspan=3)
        
        ttk.Label(main_frame, text="Enter a number:").grid(row=4, column=0, sticky=tk.W, padx=5)
        self.number_entry = ttk.Entry(main_frame, width=20)
        self.number_entry.grid(row=4, column=1, padx=5)
        self.number_entry.bind('<Return>', lambda e: self.check_single())
        
        self.check_btn = ttk.Button(main_frame, text="Check", command=self.check_single)
        self.check_btn.grid(row=4, column=2, padx=5)
        
        # Result frame
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="10")
        result_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        self.result_text = tk.Text(result_frame, height=4, width=80, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Range check section
        ttk.Separator(main_frame, orient='horizontal').grid(row=6, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(main_frame, text="Find Perfect Numbers in Range", 
                 font=('Helvetica', 12, 'bold')).grid(row=7, column=0, columnspan=3)
        
        ttk.Label(main_frame, text="Range:").grid(row=8, column=0, sticky=tk.W, padx=5)
        
        ttk.Label(main_frame, text="From:").grid(row=9, column=0, sticky=tk.W, padx=5)
        self.range_start = ttk.Entry(main_frame, width=15)
        self.range_start.grid(row=9, column=1, sticky=tk.W, padx=5)
        self.range_start.insert(0, "1")
        
        ttk.Label(main_frame, text="To:").grid(row=10, column=0, sticky=tk.W, padx=5)
        self.range_end = ttk.Entry(main_frame, width=15)
        self.range_end.grid(row=10, column=1, sticky=tk.W, padx=5)
        self.range_end.insert(0, "10000")
        
        self.find_btn = ttk.Button(main_frame, text="Find Perfect Numbers", command=self.find_in_range)
        self.find_btn.grid(row=11, column=0, columnspan=2, pady=10, sticky=tk.W, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # List of perfect numbers
        ttk.Separator(main_frame, orient='horizontal').grid(row=13, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(main_frame, text="Known Perfect Numbers", 
                 font=('Helvetica', 12, 'bold')).grid(row=14, column=0, columnspan=3)
        
        perfect_info = ttk.Label(main_frame, 
                                text="6, 28, 496, 8128, 33550336, 8589869056, 137438691328...",
                                font=('Helvetica', 9), foreground='gray')
        perfect_info.grid(row=15, column=0, columnspan=3, pady=5)
    
    def is_perfect(self, n):
        """Optimized perfect number checker using divisor sum"""
        if n <= 1:
            return False
        
        divisor_sum = 1  # 1 is always a divisor
        
        # Only check up to sqrt(n)
        i = 2
        while i * i <= n:
            if n % i == 0:
                divisor_sum += i
                if i != n // i:  # Avoid counting the square root twice
                    divisor_sum += n // i
            i += 1
        
        return divisor_sum == n
    
    def get_divisors(self, n):
        """Get all proper divisors of n"""
        if n <= 1:
            return []
        
        divisors = [1]
        i = 2
        while i * i <= n:
            if n % i == 0:
                divisors.append(i)
                if i != n // i:
                    divisors.append(n // i)
            i += 1
        
        return sorted(divisors)
    
    def check_single(self):
        """Check if a single number is perfect"""
        try:
            num = int(self.number_entry.get())
            
            if num <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive number")
                return
            
            is_perf = self.is_perfect(num)
            divisors = self.get_divisors(num)
            divisors_sum = sum(divisors)
            
            # Update result
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            
            if is_perf:
                result = f"✓ {num} IS a perfect number!\n\n"
                result += f"Divisors: {', '.join(map(str, divisors))}\n"
                result += f"Sum: {' + '.join(map(str, divisors))} = {divisors_sum}"
            else:
                result = f"✗ {num} is NOT a perfect number\n\n"
                result += f"Divisors: {', '.join(map(str, divisors))}\n"
                result += f"Sum: {' + '.join(map(str, divisors))} = {divisors_sum} (not equal to {num})"
            
            self.result_text.insert(1.0, result)
            self.result_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer")
    
    def find_in_range(self):
        """Find all perfect numbers in a given range"""
        try:
            start = int(self.range_start.get())
            end = int(self.range_end.get())
            
            if start < 1 or end < 1 or start > end:
                messagebox.showerror("Invalid Range", "Please enter valid range (start <= end, both > 0)")
                return
            
            if end - start > 1000000:
                messagebox.showwarning("Large Range", "This may take a while. Searching large ranges...")
            
            # Run in separate thread to prevent UI freezing
            thread = threading.Thread(target=self._find_perfect_numbers, args=(start, end))
            thread.start()
        
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid integers")
    
    def _find_perfect_numbers(self, start, end):
        """Helper function to find perfect numbers (runs in separate thread)"""
        self.progress.start()
        self.check_btn.config(state=tk.DISABLED)
        self.find_btn.config(state=tk.DISABLED)
        
        perfect_nums = []
        for num in range(start, end + 1):
            if self.is_perfect(num):
                perfect_nums.append(num)
        
        # Update result
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        if perfect_nums:
            result = f"Perfect numbers found in range [{start}, {end}]:\n\n"
            for num in perfect_nums:
                divisors = self.get_divisors(num)
                result += f"• {num}: {' + '.join(map(str, divisors))} = {num}\n"
        else:
            result = f"No perfect numbers found in range [{start}, {end}]"
        
        self.result_text.insert(1.0, result)
        self.result_text.config(state=tk.DISABLED)
        
        self.progress.stop()
        self.check_btn.config(state=tk.NORMAL)
        self.find_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = PerfectNumberChecker(root)
    root.mainloop()
