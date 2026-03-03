/**
 * SynthInk Theme System - JavaScript Module
 * 模块化主题系统 - 粒子效果与主题管理
 * 
 * 彩蛋：Trans-Am系统，启动！GN粒子散布开始 ♪
 */

(function() {
    'use strict';

    // 主题配置
    const THEMES = [
        { id: 'dark', name: '暗色', category: '基础' },
        { id: 'light', name: '亮色', category: '基础' },
        { id: 'cyberpunk', name: '赛博朋克', category: '氛围' },
        { id: 'sakura', name: '樱花', category: '氛围' },
        { id: 'ocean', name: '深海', category: '氛围' },
        { id: 'midnight', name: '午夜', category: '氛围' },
        { id: 'forest', name: '森林', category: '氛围' },
        { id: 'bamboo', name: '竹林绿', category: '自然' },
        { id: 'mint-choco', name: '薄荷巧克力', category: '甜品' },
        { id: 'strawberry-cream', name: '草莓奶油', category: '甜品' },
        { id: 'orange-soda', name: '香橙气泡', category: '饮品' },
        { id: 'mygo-light', name: '星歌', category: '音乐' },
        { id: 'bangdream-dark', name: '夜奏', category: '音乐' },
        { id: 'exia', name: '能天使', category: '高达' },
        { id: 'veda', name: 'VEDA', category: '高达' },
        { id: 'twins', name: '双子', category: '高达' }
    ];

    // 主题管理器
    const ThemeManager = {
        currentTheme: 'dark',
        
        init() {
            // 从localStorage读取保存的主题
            const savedTheme = localStorage.getItem('synthink-theme');
            if (savedTheme && THEMES.some(t => t.id === savedTheme)) {
                this.currentTheme = savedTheme;
            }
            this.applyTheme(this.currentTheme);
            this.createThemeSelector();
        },

        applyTheme(themeId) {
            document.documentElement.setAttribute('data-theme', themeId);
            this.currentTheme = themeId;
            localStorage.setItem('synthink-theme', themeId);
            
            // 触发主题切换事件
            window.dispatchEvent(new CustomEvent('themechange', { 
                detail: { theme: themeId } 
            }));

            // 更新粒子系统
            if (window.ParticleSystem) {
                ParticleSystem.updateParticleType();
            }

            // 更新矩阵雨效果
            if (window.EffectsManager) {
                EffectsManager.handleThemeChange(themeId);
            }
        },

        createThemeSelector() {
            const selector = document.querySelector('.theme-select');
            if (!selector) return;

            // 按分类组织主题
            const categories = {};
            THEMES.forEach(theme => {
                if (!categories[theme.category]) {
                    categories[theme.category] = [];
                }
                categories[theme.category].push(theme);
            });

            // 生成分组选项
            selector.innerHTML = '';
            for (const [category, themes] of Object.entries(categories)) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = category;
                
                themes.forEach(theme => {
                    const option = document.createElement('option');
                    option.value = theme.id;
                    option.textContent = theme.name;
                    if (theme.id === this.currentTheme) {
                        option.selected = true;
                    }
                    optgroup.appendChild(option);
                });
                
                selector.appendChild(optgroup);
            }

            // 绑定切换事件
            selector.addEventListener('change', (e) => {
                this.applyTheme(e.target.value);
            });
        }
    };

    // 粒子系统
    const ParticleSystem = {
        canvas: null,
        ctx: null,
        particles: [],
        animationId: null,
        particleType: 'floating',

        init() {
            this.canvas = document.getElementById('particle-canvas');
            if (!this.canvas) return;

            this.ctx = this.canvas.getContext('2d');
            this.resize();
            this.updateParticleType();
            this.createParticles();
            this.animate();

            // 监听窗口大小变化
            window.addEventListener('resize', () => {
                this.resize();
                this.createParticles();
            });

            // 监听主题切换
            window.addEventListener('themechange', () => {
                this.updateParticleType();
                this.createParticles();
            });
        },

        resize() {
            if (!this.canvas) return;
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        },

        updateParticleType() {
            const style = getComputedStyle(document.body);
            this.particleType = style.getPropertyValue('--particle-type').trim() || 'floating';
        },

        createParticles() {
            const particleCount = window.innerWidth < 768 ? 25 : 50;
            this.particles = [];
            for (let i = 0; i < particleCount; i++) {
                this.particles.push(new Particle(this.particleType, this.canvas));
            }
        },

        animate() {
            if (!this.ctx) return;
            
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            
            this.particles.forEach(particle => {
                particle.update(this.canvas);
                particle.draw(this.ctx);
            });
            
            this.animationId = requestAnimationFrame(() => this.animate());
        }
    };

    // 粒子类
    class Particle {
        constructor(type, canvas) {
            this.type = type;
            this.reset(canvas);
        }

        reset(canvas) {
            const style = getComputedStyle(document.body);
            
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 3 + 1;
            this.opacity = Math.random() * 0.5 + 0.2;
            this.color = style.getPropertyValue('--particle-color').trim() || '#52b788';
            this.baseOpacity = parseFloat(style.getPropertyValue('--particle-opacity')) || 0.5;
            this.life = 0;
            this.maxLife = Math.random() * 200 + 100;

            switch(this.type) {
                case 'firefly':
                    this.speedX = (Math.random() - 0.5) * 0.8;
                    this.speedY = (Math.random() - 0.5) * 0.8;
                    this.flashSpeed = Math.random() * 0.05 + 0.02;
                    this.flashPhase = Math.random() * Math.PI * 2;
                    break;
                case 'sakura':
                    this.speedX = (Math.random() - 0.5) * 1.2;
                    this.speedY = Math.random() * 0.6 + 0.3;
                    this.rotation = Math.random() * Math.PI * 2;
                    this.rotationSpeed = (Math.random() - 0.5) * 0.04;
                    this.swayAmplitude = Math.random() * 30 + 20;
                    this.swayPhase = Math.random() * Math.PI * 2;
                    break;
                case 'bubble':
                    this.speedX = (Math.random() - 0.5) * 0.3;
                    this.speedY = -(Math.random() * 0.4 + 0.15);
                    this.wobble = Math.random() * Math.PI * 2;
                    this.wobbleSpeed = Math.random() * 0.03 + 0.01;
                    break;
                case 'rising':
                    this.speedX = (Math.random() - 0.5) * 0.2;
                    this.speedY = -(Math.random() * 1.2 + 0.6);
                    break;
                case 'wireframe':
                    this.speedX = Math.random() * 4 + 3;
                    this.speedY = (Math.random() - 0.5) * 0.5;
                    this.length = Math.random() * 25 + 10;
                    this.x = Math.random() * (canvas.width + 400) - 200;
                    this.y = Math.random() * canvas.height;
                    break;
                case 'datastream':
                    this.speedX = 0;
                    this.speedY = Math.random() * 2 + 1;
                    this.length = Math.random() * 30 + 10;
                    this.char = String.fromCharCode(0x30A0 + Math.floor(Math.random() * 96));
                    break;
                case 'twinparticle':
                    this.speedX = (Math.random() - 0.5) * 1.5;
                    this.speedY = (Math.random() - 0.5) * 1.5;
                    this.isGold = Math.random() > 0.5;
                    break;
                case 'creamy':
                    this.speedX = (Math.random() - 0.5) * 0.3;
                    this.speedY = (Math.random() - 0.5) * 0.3;
                    this.pulsePhase = Math.random() * Math.PI * 2;
                    this.pulseSpeed = Math.random() * 0.02 + 0.01;
                    this.baseSize = this.size;
                    break;
                case 'musical':
                    this.speedX = (Math.random() - 0.5) * 0.8;
                    this.speedY = -Math.random() * 0.5 - 0.2;
                    this.noteType = Math.floor(Math.random() * 3);
                    this.rotation = Math.random() * Math.PI * 2;
                    this.rotationSpeed = (Math.random() - 0.5) * 0.03;
                    this.swayPhase = Math.random() * Math.PI * 2;
                    break;
                case 'spotlight':
                    this.speedX = 0;
                    this.speedY = 0;
                    this.targetX = Math.random() * canvas.width;
                    this.targetY = Math.random() * canvas.height;
                    this.moveSpeed = Math.random() * 0.5 + 0.2;
                    this.beamWidth = Math.random() * 40 + 20;
                    this.beamOpacity = 0;
                    this.fadePhase = Math.random() * Math.PI * 2;
                    this.fadeSpeed = Math.random() * 0.02 + 0.01;
                    break;
                default: // floating
                    this.speedX = (Math.random() - 0.5) * 0.5;
                    this.speedY = (Math.random() - 0.5) * 0.5;
            }
        }

        update(canvas) {
            this.life++;

            switch(this.type) {
                case 'firefly':
                    this.x += this.speedX;
                    this.y += this.speedY;
                    this.flashPhase += this.flashSpeed;
                    this.opacity = this.baseOpacity * (0.5 + 0.5 * Math.sin(this.flashPhase));
                    if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
                        this.reset(canvas);
                    }
                    break;
                case 'sakura':
                    this.swayPhase += 0.02;
                    this.x += this.speedX + Math.sin(this.swayPhase) * 0.3;
                    this.y += this.speedY;
                    this.rotation += this.rotationSpeed;
                    if (this.y > canvas.height + 20 || this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                case 'bubble':
                    this.wobble += this.wobbleSpeed;
                    this.x += this.speedX + Math.sin(this.wobble) * 0.3;
                    this.y += this.speedY;
                    this.opacity = this.baseOpacity * (0.7 + 0.3 * Math.sin(this.wobble));
                    if (this.y < -20 || this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                case 'rising':
                    this.x += this.speedX;
                    this.y += this.speedY;
                    this.opacity = this.baseOpacity * Math.min(1, this.life / 30);
                    if (this.y < -20 || this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                case 'wireframe':
                    this.x += this.speedX;
                    this.y += this.speedY;
                    if (this.x > canvas.width + 50) {
                        this.reset(canvas);
                    }
                    break;
                case 'datastream':
                    this.y += this.speedY;
                    if (this.y > canvas.height || this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                case 'twinparticle':
                    this.x += this.speedX;
                    this.y += this.speedY;
                    this.color = this.isGold ? '#ffd700' : '#00bfff';
                    if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height || this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                case 'creamy':
                    this.x += this.speedX;
                    this.y += this.speedY;
                    this.pulsePhase += this.pulseSpeed;
                    this.size = this.baseSize * (1 + Math.sin(this.pulsePhase) * 0.3);
                    this.opacity = this.baseOpacity * (0.6 + 0.4 * Math.sin(this.pulsePhase));
                    if (this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                case 'musical':
                    this.swayPhase += 0.03;
                    this.x += this.speedX + Math.sin(this.swayPhase) * 0.5;
                    this.y += this.speedY;
                    this.rotation += this.rotationSpeed;
                    this.opacity = this.baseOpacity * Math.max(0, 1 - this.life / this.maxLife);
                    if (this.y < -20 || this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                case 'spotlight':
                    this.x += (this.targetX - this.x) * this.moveSpeed * 0.02;
                    this.y += (this.targetY - this.y) * this.moveSpeed * 0.02;
                    this.fadePhase += this.fadeSpeed;
                    this.beamOpacity = 0.15 + 0.1 * Math.sin(this.fadePhase);
                    if (Math.abs(this.x - this.targetX) < 5 && Math.abs(this.y - this.targetY) < 5) {
                        this.targetX = Math.random() * canvas.width;
                        this.targetY = Math.random() * canvas.height;
                    }
                    if (this.life > this.maxLife) {
                        this.reset(canvas);
                    }
                    break;
                default: // floating
                    this.x += this.speedX;
                    this.y += this.speedY;
                    if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
                        this.reset(canvas);
                    }
            }
        }

        draw(ctx) {
            ctx.save();

            switch(this.type) {
                case 'firefly':
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = this.color;
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                    break;
                case 'sakura':
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = this.color;
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.rotation);
                    ctx.beginPath();
                    ctx.ellipse(0, 0, this.size * 2, this.size, 0, 0, Math.PI * 2);
                    ctx.fill();
                    break;
                case 'bubble':
                    ctx.globalAlpha = this.opacity * 0.6;
                    ctx.strokeStyle = this.color;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.globalAlpha = this.opacity * 0.3;
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x - this.size, this.y - this.size, this.size * 0.5, 0, Math.PI * 2);
                    ctx.fill();
                    break;
                case 'wireframe':
                    ctx.globalAlpha = this.opacity * 0.8;
                    ctx.strokeStyle = this.color;
                    ctx.lineWidth = 1.5;
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = this.color;
                    ctx.beginPath();
                    ctx.moveTo(this.x, this.y);
                    ctx.lineTo(this.x - this.length, this.y);
                    ctx.stroke();
                    break;
                case 'datastream':
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = this.color;
                    ctx.font = `${this.size * 4}px monospace`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.shadowBlur = 5;
                    ctx.shadowColor = this.color;
                    ctx.fillText(this.char, this.x, this.y);
                    break;
                case 'twinparticle':
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = this.color;
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                    break;
                case 'creamy':
                    ctx.globalAlpha = this.opacity * 0.7;
                    ctx.fillStyle = this.color;
                    ctx.shadowBlur = 20;
                    ctx.shadowColor = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size * 2, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.4, 0, Math.PI * 2);
                    ctx.fill();
                    break;
                case 'musical':
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = this.color;
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = this.color;
                    ctx.translate(this.x, this.y);
                    ctx.rotate(this.rotation);
                    const notes = ['♪', '♫', '♬'];
                    ctx.font = `${this.size * 3}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(notes[this.noteType], 0, 0);
                    ctx.rotate(-this.rotation);
                    ctx.translate(-this.x, -this.y);
                    break;
                case 'spotlight':
                    const gradient = ctx.createRadialGradient(
                        this.x, this.y, 0,
                        this.x, this.y, this.beamWidth
                    );
                    gradient.addColorStop(0, `rgba(255, 255, 255, ${this.beamOpacity})`);
                    gradient.addColorStop(0.5, `rgba(255, 255, 255, ${this.beamOpacity * 0.3})`);
                    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                    ctx.globalAlpha = 1;
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.beamWidth, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.globalAlpha = this.beamOpacity * 2;
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
                    break;
                default: // floating
                    ctx.globalAlpha = this.opacity;
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                    ctx.fill();
            }

            ctx.restore();
        }
    }

    // 特效管理器
    const EffectsManager = {
        matrixRain: null,
        matrixInterval: null,

        init() {
            this.matrixRain = document.getElementById('matrix-rain');
        },

        handleThemeChange(themeId) {
            // 矩阵雨效果只在赛博朋克主题显示
            if (this.matrixRain) {
                if (themeId === 'cyberpunk') {
                    this.startMatrixRain();
                } else {
                    this.stopMatrixRain();
                }
            }
        },

        startMatrixRain() {
            if (!this.matrixRain) return;
            this.matrixRain.classList.add('active');
            
            if (this.matrixInterval) return;

            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*';
            
            this.matrixInterval = setInterval(() => {
                if (!this.matrixRain.classList.contains('active')) return;
                
                const column = document.createElement('div');
                column.className = 'matrix-column';
                column.style.left = Math.random() * 100 + '%';
                column.style.animationDuration = (Math.random() * 3 + 5) + 's';
                column.style.animationDelay = Math.random() * 2 + 's';
                
                let text = '';
                for (let i = 0; i < 20; i++) {
                    text += chars[Math.floor(Math.random() * chars.length)] + '<br>';
                }
                column.innerHTML = text;
                
                this.matrixRain.appendChild(column);
                
                setTimeout(() => {
                    if (column.parentNode) {
                        column.parentNode.removeChild(column);
                    }
                }, 8000);
            }, 200);
        },

        stopMatrixRain() {
            if (!this.matrixRain) return;
            this.matrixRain.classList.remove('active');
            
            if (this.matrixInterval) {
                clearInterval(this.matrixInterval);
                this.matrixInterval = null;
            }
            
            this.matrixRain.innerHTML = '';
        }
    };

    // 暴露到全局
    window.ThemeManager = ThemeManager;
    window.ParticleSystem = ParticleSystem;
    window.EffectsManager = EffectsManager;

    // DOM加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            ThemeManager.init();
            ParticleSystem.init();
            EffectsManager.init();
        });
    } else {
        ThemeManager.init();
        ParticleSystem.init();
        EffectsManager.init();
    }

})();
