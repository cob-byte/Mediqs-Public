document.addEventListener('DOMContentLoaded', function () {
    let primaryTabs = document.querySelectorAll('.tabs_wrap > ul > li[data-tabs]');
    let primaryContents = document.querySelectorAll('.tabs_content[id^="overall"], .tabs_content[id^="healthcenter"]');
    let pageTitle = document.querySelector('.title');
  
    primaryTabs.forEach(tab => {
      tab.addEventListener('click', function () {
        let tabID = this.getAttribute('data-tabs');
        let title = this.getAttribute('data-title');
  
        // Set the active tab
        primaryTabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
  
        // Show the content of the active tab
        primaryContents.forEach(content => {
          if (content.id === tabID) {
            content.style.display = 'block';
  
            // Set the page title according to the active tab
            switch (tabID) {
              case 'overall':
                pageTitle.innerText = 'Disease Statistics of All Healthcenters';
                break;
              case 'healthcenter':
                pageTitle.innerText = title;
                break;
              case 'outbreak':
                pageTitle.innerText = 'Disease Statistics';
                break;
            }
  
          } else {
            content.style.display = 'none';
          }
        });
      });
    });
  
    // Set the initial active tab and its content
    if (primaryTabs.length > 0) {
      primaryTabs[0].click();
    }
  
    // Handle the nested tabs
    let nestedTabs = document.querySelectorAll('.tabs_wrap > ul > li[data-tabs1]');
    let nestedContents = document.querySelectorAll('.tabs_content[id^="all_time"], .tabs_content[id^="30_days"], .tabs_content[id^="7_days"], .tabs_content[id^="1_day"]');
  
    nestedTabs.forEach(tab => {
      tab.addEventListener('click', function () {
        let nestedTabID = this.getAttribute('data-tabs1');
  
        // Set the active nested tab
        nestedTabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
  
        // Show the content of the active nested tab
        nestedContents.forEach(content => {
          if (content.id === nestedTabID) {
            content.style.display = 'block';
          } else {
            content.style.display = 'none';
          }
        });
      });
    });
  
    // Set the initial active nested tab and its content
    if (nestedTabs.length > 0) {
      nestedTabs[0].click();
    }

    let nestedTabs1 = document.querySelectorAll('.tabs_wrap > ul > li[data-tabs2]');
    let nestedContents1 = document.querySelectorAll('.tabs_content1[id^="all_time"], .tabs_content1[id^="30_days"], .tabs_content1[id^="7_days"], .tabs_content1[id^="1_day"]');
  
    nestedTabs1.forEach(tab1 => {
      tab1.addEventListener('click', function () {
        let nestedTabID1 = this.getAttribute('data-tabs2');
  
        // Set the active nested tab
        nestedTabs1.forEach(t => t.classList.remove('active'));
        this.classList.add('active');
  
        // Show the content of the active nested tab
        nestedContents1.forEach(content1 => {
          if (content1.id === nestedTabID1) {
            content1.style.display = 'block';
          } else {
            content1.style.display = 'none';
          }
        });
      });
    });
  
    // Set the initial active nested tab and its content
    if (nestedTabs1.length > 0) {
      nestedTabs1[0].click();
    }
  });
  