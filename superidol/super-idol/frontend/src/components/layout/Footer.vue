<template>
  <footer class="app-footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-logo">
          <span class="logo-text">速per Idol</span>
          <p class="slogan">Healthy Life Starts with Nutrition</p>
        </div>
        
        <div class="footer-links">
          <div class="link-section">
            <h3>About Us</h3>
            <ul>
              <li><a href="#about">About 速per Idol</a></li>
              <li><a href="#team">Our Team</a></li>
              <li><a href="#contact">Contact Us</a></li>
            </ul>
          </div>
          
          <div class="link-section">
            <h3>User Guide</h3>
            <ul>
              <li><a href="#guide">Operation Guide</a></li>
              <li><a href="#faq">FAQ</a></li>
              <li><a href="#support">Support</a></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="footer-bottom">
        <div class="social-icons">
          <a href="#" title="Facebook"><i class="fab fa-facebook-f"></i></a>
          <a href="#" title="Instagram"><i class="fab fa-instagram"></i></a>
          <a href="#" title="Twitter"><i class="fab fa-twitter"></i></a>
          <a href="#" title="GitHub"><i class="fab fa-github"></i></a>
        </div>
        
        <div class="copyright">
          &copy; {{ currentYear }} 速per Idol - DBMS Team 11302. All Rights Reserved.
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
}
</script>

<style scoped>
.app-footer {
  background-color: #333;
  color: #fff;
  padding: 40px 0 20px;
  margin-top: auto;
}

.footer-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 40px;
}

.footer-logo {
  margin-bottom: 30px;
  flex: 1 1 100%;
}

@media (min-width: 768px) {
  .footer-logo {
    flex: 0 0 30%;
  }
}

.logo-text {
  display: block;
  font-family: var(--font-tc), var(--font-en);
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
}

.slogan {
  font-size: 14px;
  color: #aaa;
  font-family: var(--font-tc), var(--font-en);
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  flex: 1 1 100%;
}

@media (min-width: 768px) {
  .footer-links {
    flex: 0 0 60%;
    justify-content: flex-end;
  }
}

.link-section {
  flex: 1 1 200px;
}

.link-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 15px;
  color: #fff;
  font-family: var(--font-tc), var(--font-en);
}

.link-section ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.link-section li {
  margin-bottom: 10px;
}

.link-section a {
  color: #bbb;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s;
  font-family: var(--font-tc), var(--font-en);
}

.link-section a:hover {
  color: var(--primary-color);
}

.footer-bottom {
  padding-top: 20px;
  border-top: 1px solid #444;
  display: flex;
  flex-direction: column;
  align-items: center;
}

@media (min-width: 768px) {
  .footer-bottom {
    flex-direction: row;
    justify-content: space-between;
  }
}

.social-icons {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

@media (min-width: 768px) {
  .social-icons {
    margin-bottom: 0;
  }
}

.social-icons a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background-color: #444;
  border-radius: 50%;
  color: #fff;
  transition: all 0.3s;
}

.social-icons a:hover {
  background-color: var(--primary-color);
  transform: translateY(-3px);
}

.copyright {
  font-size: 13px;
  color: #999;
  text-align: center;
  font-family: var(--font-tc), var(--font-en);
}
</style> 