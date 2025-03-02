// وظائف تشغيل عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تفعيل الوضع الداكن إذا كان مخزنًا
    initDarkMode();
    
    // تفعيل تشغيل الفيديو التلقائي
    initVideoAutoplay();
    
    // تفعيل التمرير السلس
    initSmoothScrolling();
});

// وظيفة تهيئة الوضع الداكن
function initDarkMode() {
    // التحقق مما إذا كان المستخدم قد اختار الوضع الداكن سابقًا
    const isDarkMode = localStorage.getItem('darkMode') === 'enabled';
    
    // تطبيق الوضع الداكن إذا كان مفعلًا
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        
        // تحديث حالة مفتاح التبديل في صفحة الملف الشخصي إذا كان موجودًا
        const darkModeToggle = document.querySelector('#darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.checked = true;
        }
    }
    
    // إضافة زر تبديل الوضع الداكن في الزاوية العلوية
    addDarkModeToggle();
}

// إضافة زر تبديل الوضع الداكن
function addDarkModeToggle() {
    // إنشاء زر التبديل
    const toggleButton = document.createElement('button');
    toggleButton.className = 'dark-mode-toggle';
    toggleButton.innerHTML = '<i class="fas fa-moon"></i>';
    toggleButton.title = 'تبديل الوضع الداكن';
    
    // تحديث أيقونة الزر بناءً على الوضع الحالي
    if (document.body.classList.contains('dark-mode')) {
        toggleButton.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    // إضافة نمط للزر
    toggleButton.style.position = 'fixed';
    toggleButton.style.top = '15px';
    toggleButton.style.left = '15px';
    toggleButton.style.zIndex = '1000';
    toggleButton.style.background = 'var(--card-bg-color)';
    toggleButton.style.border = 'none';
    toggleButton.style.borderRadius = '50%';
    toggleButton.style.width = '40px';
    toggleButton.style.height = '40px';
    toggleButton.style.boxShadow = '0 2px 5px var(--shadow-color)';
    toggleButton.style.cursor = 'pointer';
    toggleButton.style.color = 'var(--primary-color)';
    toggleButton.style.fontSize = '18px';
    toggleButton.style.display = 'flex';
    toggleButton.style.alignItems = 'center';
    toggleButton.style.justifyContent = 'center';
    toggleButton.style.transition = 'all 0.3s ease';
    
    // إضافة حدث النقر
    toggleButton.addEventListener('click', function() {
        toggleDarkMode();
        
        // تحديث أيقونة الزر
        if (document.body.classList.contains('dark-mode')) {
            this.innerHTML = '<i class="fas fa-sun"></i>';
        } else {
            this.innerHTML = '<i class="fas fa-moon"></i>';
        }
    });
    
    // إضافة الزر إلى الصفحة
    document.body.appendChild(toggleButton);
}

// وظيفة تبديل الوضع الداكن
function toggleDarkMode() {
    if (document.body.classList.contains('dark-mode')) {
        // تعطيل الوضع الداكن
        document.body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'disabled');
        
        // تحديث حالة مفتاح التبديل في صفحة الملف الشخصي إذا كان موجودًا
        const darkModeToggle = document.querySelector('#darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.checked = false;
        }
    } else {
        // تفعيل الوضع الداكن
        document.body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'enabled');
        
        // تحديث حالة مفتاح التبديل في صفحة الملف الشخصي إذا كان موجودًا
        const darkModeToggle = document.querySelector('#darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.checked = true;
        }
    }
}

// وظيفة تهيئة تشغيل الفيديو التلقائي
function initVideoAutoplay() {
    // البحث عن جميع عناصر الفيديو في الصفحة
    const videos = document.querySelectorAll('video');
    
    // إعداد مراقب التقاطع لتشغيل الفيديو عندما يكون مرئيًا
    if (videos.length > 0 && 'IntersectionObserver' in window) {
        const videoObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // تشغيل الفيديو عندما يكون مرئيًا
                    entry.target.play();
                } else {
                    // إيقاف الفيديو عندما يكون غير مرئي
                    entry.target.pause();
                }
            });
        }, { threshold: 0.6 }); // تشغيل عندما يكون 60% من الفيديو مرئيًا
        
        // مراقبة جميع عناصر الفيديو
        videos.forEach(video => {
            videoObserver.observe(video);
        });
    }
}

// وظيفة تهيئة التمرير السلس
function initSmoothScrolling() {
    // تطبيق التمرير السلس على جميع الروابط الداخلية
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}
