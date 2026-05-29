// Global Application State
let parsedContacts = [];
let selectedExcelFile = null;
let currentTab = 'vcf2excel';

// Document Elements
const vcfDropzone = document.getElementById('vcf-dropzone');
const excelDropzone = document.getElementById('excel-dropzone');
const vcfFileInput = document.getElementById('vcf-file-input');
const excelFileInput = document.getElementById('excel-file-input');

// VCF Target select mapping options
const mappingOptions = [
    { value: '', text: '— Skip Column —' },
    { value: 'display_name', text: 'Display Name (Full Name)' },
    { value: 'first_name', text: 'First Name' },
    { value: 'middle_name', text: 'Middle Name' },
    { value: 'last_name', text: 'Last Name' },
    { value: 'prefix', text: 'Prefix (e.g. Mr.)' },
    { value: 'suffix', text: 'Suffix (e.g. Jr.)' },
    { value: 'org', text: 'Organization' },
    { value: 'department', text: 'Department' },
    { value: 'title', text: 'Job Title' },
    { value: 'bday', text: 'Birthday' },
    { value: 'note', text: 'Notes' },
    { value: 'phone_cell', text: 'Phone - Mobile' },
    { value: 'phone_work', text: 'Phone - Work' },
    { value: 'phone_home', text: 'Phone - Home' },
    { value: 'phone_other', text: 'Phone - Other' },
    { value: 'email_home', text: 'Email - Home' },
    { value: 'email_work', text: 'Email - Work' },
    { value: 'email_other', text: 'Email - Other' },
    { value: 'address_home_street', text: 'Home Address - Street' },
    { value: 'address_home_city', text: 'Home Address - City' },
    { value: 'address_home_region', text: 'Home Address - State/Region' },
    { value: 'address_home_zip', text: 'Home Address - Zip Code' },
    { value: 'address_home_country', text: 'Home Address - Country' },
    { value: 'address_work_street', text: 'Work Address - Street' },
    { value: 'address_work_city', text: 'Work Address - City' },
    { value: 'address_work_region', text: 'Work Address - State/Region' },
    { value: 'address_work_zip', text: 'Work Address - Zip Code' },
    { value: 'address_work_country', text: 'Work Address - Country' },
    { value: 'url_other', text: 'Website' }
];

// Initialize listeners
document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop(vcfDropzone, vcfFileInput, handleVcfFile);
    setupDragAndDrop(excelDropzone, excelFileInput, handleExcelFile);
});

// Tab navigation switcher
function switchTab(tabName) {
    currentTab = tabName;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    document.getElementById(`tab-${tabName}`).classList.add('active');
    document.getElementById(`section-${tabName}`).classList.add('active');
}

// Set up drag & drop listeners
function setupDragAndDrop(dropzone, fileInput, fileHandler) {
    dropzone.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileHandler(e.target.files[0]);
        }
    });
    
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
        if (dropzone.id === 'excel-dropzone') {
            dropzone.classList.add('dragover-secondary');
        }
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover', 'dragover-secondary');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover', 'dragover-secondary');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            fileHandler(e.dataTransfer.files[0]);
        }
    });
}

// Show/Hide Helpers
function hideElement(id) {
    document.getElementById(id).classList.add('hidden');
}

function showElement(id) {
    document.getElementById(id).classList.remove('hidden');
}

// -------------------------------------------------------------
// VCF TO EXCEL FLOW
// -------------------------------------------------------------

function handleVcfFile(file) {
    if (!file.name.endsWith('.vcf')) {
        showVcfError('Please upload a valid .vcf vCard file.');
        return;
    }
    
    hideElement('vcf-error');
    hideElement('vcf-preview-area');
    showElement('vcf-loading');
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/vcf-to-json', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideElement('vcf-loading');
        if (data.error) {
            showVcfError(data.error);
        } else {
            parsedContacts = data.contacts;
            renderContactsTable();
            showElement('vcf-preview-area');
        }
    })
    .catch(err => {
        hideElement('vcf-loading');
        showVcfError('An error occurred while uploading. Please ensure the server is running.');
        console.error(err);
    });
}

function showVcfError(msg) {
    const errorEl = document.getElementById('vcf-error');
    errorEl.querySelector('.alert-message').textContent = msg;
    errorEl.classList.remove('hidden');
}

// Render the VCF contacts preview table
function renderContactsTable() {
    const tbody = document.getElementById('contacts-table-body');
    tbody.innerHTML = '';
    
    if (parsedContacts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">No contacts available. Click "Add Contact" to create one.</td></tr>`;
        updateTableSummary(0, 0);
        return;
    }
    
    parsedContacts.forEach((contact, index) => {
        const tr = document.createElement('tr');
        tr.dataset.index = index;
        tr.className = 'contact-row';
        
        // 1. Name Cell
        const nameCell = document.createElement('td');
        nameCell.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                <input type="text" class="table-input" style="font-weight: 600;" placeholder="Display Name" value="${contact.display_name || ''}" oninput="updateField(${index}, 'display_name', this.value)">
                <div style="display: flex; gap: 0.25rem;">
                    <input type="text" class="table-input" placeholder="First" value="${contact.first_name || ''}" oninput="updateField(${index}, 'first_name', this.value)" style="font-size: 0.75rem;">
                    <input type="text" class="table-input" placeholder="Last" value="${contact.last_name || ''}" oninput="updateField(${index}, 'last_name', this.value)" style="font-size: 0.75rem;">
                </div>
            </div>
        `;
        tr.appendChild(nameCell);
        
        // 2. Org & Title Cell
        const orgCell = document.createElement('td');
        orgCell.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                <input type="text" class="table-input" placeholder="Company" value="${contact.org || ''}" oninput="updateField(${index}, 'org', this.value)">
                <input type="text" class="table-input" placeholder="Job Title" value="${contact.title || ''}" oninput="updateField(${index}, 'title', this.value)" style="font-size: 0.75rem; color: var(--text-secondary);">
            </div>
        `;
        tr.appendChild(orgCell);
        
        // 3. Phones Cell
        const phoneCell = document.createElement('td');
        phoneCell.innerHTML = renderMultiValueField(index, 'phones', contact.phones || []);
        tr.appendChild(phoneCell);
        
        // 4. Emails Cell
        const emailCell = document.createElement('td');
        emailCell.innerHTML = renderMultiValueField(index, 'emails', contact.emails || []);
        tr.appendChild(emailCell);
        
        // 5. Address Cell (Editable simplified primary address)
        const addrCell = document.createElement('td');
        const primaryAddr = contact.addresses && contact.addresses[0] ? contact.addresses[0] : { street: '', city: '', region: '', zip: '', country: '', types: [] };
        addrCell.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                <input type="text" class="table-input" placeholder="Street" value="${primaryAddr.street || ''}" oninput="updateAddress(${index}, 0, 'street', this.value)" style="font-size: 0.8rem;">
                <div style="display: flex; gap: 0.25rem;">
                    <input type="text" class="table-input" placeholder="City" value="${primaryAddr.city || ''}" oninput="updateAddress(${index}, 0, 'city', this.value)" style="font-size: 0.75rem;">
                    <input type="text" class="table-input" placeholder="Country" value="${primaryAddr.country || ''}" oninput="updateAddress(${index}, 0, 'country', this.value)" style="font-size: 0.75rem;">
                </div>
            </div>
        `;
        tr.appendChild(addrCell);
        
        // 6. Notes Cell
        const notesCell = document.createElement('td');
        notesCell.innerHTML = `
            <textarea class="table-input" rows="2" style="resize: vertical; font-size: 0.8rem;" placeholder="Notes..." oninput="updateField(${index}, 'note', this.value)">${contact.note || ''}</textarea>
        `;
        tr.appendChild(notesCell);
        
        // 7. Action Cell
        const actionCell = document.createElement('td');
        actionCell.innerHTML = `
            <button class="btn-icon" onclick="deleteContact(${index})" title="Delete Contact">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        `;
        tr.appendChild(actionCell);
        
        tbody.appendChild(tr);
    });
    
    updateTableSummary(parsedContacts.length, parsedContacts.length);
}

// HTML generator for multi-value fields (Phones/Emails)
function renderMultiValueField(contactIndex, fieldKey, items) {
    let html = `<div id="mv-${fieldKey}-${contactIndex}" style="display:flex; flex-direction:column; gap:0.25rem;">`;
    
    items.forEach((item, itemIdx) => {
        const label = item.types && item.types.length > 0 ? item.types[0] : 'Other';
        html += `
            <div class="list-cell-item">
                <span class="cell-tag">${label}</span>
                <input type="text" class="table-input" value="${item.value || ''}" 
                    oninput="updateMultiValue(${contactIndex}, '${fieldKey}', ${itemIdx}, this.value)" style="font-size: 0.8rem;">
                <button onclick="deleteMultiValue(${contactIndex}, '${fieldKey}', ${itemIdx})" 
                    style="background:none; border:none; color:var(--error-color); cursor:pointer; font-size:0.75rem;"><i class="fa-solid fa-xmark"></i></button>
            </div>
        `;
    });
    
    html += `
        <button class="btn-cell-add" onclick="addMultiValueField(${contactIndex}, '${fieldKey}')">
            <i class="fa-solid fa-plus"></i> Add ${fieldKey === 'phones' ? 'Phone' : 'Email'}
        </button>
    </div>`;
    return html;
}

// Inline updates of state
function updateField(index, key, val) {
    parsedContacts[index][key] = val;
}

function updateMultiValue(contactIdx, fieldKey, itemIdx, value) {
    parsedContacts[contactIdx][fieldKey][itemIdx].value = value;
}

function deleteMultiValue(contactIdx, fieldKey, itemIdx) {
    parsedContacts[contactIdx][fieldKey].splice(itemIdx, 1);
    renderContactsTable();
}

function addMultiValueField(contactIdx, fieldKey) {
    const typeLabel = fieldKey === 'phones' ? 'CELL' : 'HOME';
    parsedContacts[contactIdx][fieldKey].push({
        value: '',
        types: [typeLabel]
    });
    renderContactsTable();
}

function updateAddress(contactIdx, addrIdx, fieldKey, val) {
    if (!parsedContacts[contactIdx].addresses) {
        parsedContacts[contactIdx].addresses = [];
    }
    if (!parsedContacts[contactIdx].addresses[addrIdx]) {
        parsedContacts[contactIdx].addresses[addrIdx] = { street: '', city: '', region: '', zip: '', country: '', types: ['HOME'] };
    }
    parsedContacts[contactIdx].addresses[addrIdx][fieldKey] = val;
}

function deleteContact(index) {
    parsedContacts.splice(index, 1);
    renderContactsTable();
}

function addContactRow() {
    parsedContacts.unshift({
        first_name: '',
        middle_name: '',
        last_name: '',
        prefix: '',
        suffix: '',
        display_name: '',
        org: '',
        department: '',
        title: '',
        bday: '',
        note: '',
        phones: [{ value: '', types: ['CELL'] }],
        emails: [{ value: '', types: ['HOME'] }],
        addresses: [],
        urls: [],
        custom: []
    });
    renderContactsTable();
    // Scroll to top of table wrapper
    document.querySelector('.contacts-table-wrapper').scrollTop = 0;
}

function updateTableSummary(shownCount, totalCount) {
    document.getElementById('contacts-summary').textContent = `Showing ${shownCount} of ${totalCount} contacts`;
}

// Client-side search filters
function filterContactsTable() {
    const rows = document.querySelectorAll('.contact-row');
    let shownCount = 0;
    
    rows.forEach(row => {
        const index = parseInt(row.dataset.index);
        const contact = parsedContacts[index];
        
        const textToSearch = [
            contact.display_name,
            contact.first_name,
            contact.last_name,
            contact.org,
            contact.title,
            contact.note,
            ...(contact.phones || []).map(p => p.value),
            ...(contact.emails || []).map(e => e.value)
        ].join(' ').toLowerCase();
        
        const qClean = document.getElementById('contact-search').value.trim().toLowerCase();
        
        if (textToSearch.includes(qClean)) {
            row.classList.remove('hidden');
            shownCount++;
        } else {
            row.classList.add('hidden');
        }
    });
    
    updateTableSummary(shownCount, parsedContacts.length);
}

// Trigger Excel download
function exportToExcel() {
    if (parsedContacts.length === 0) {
        alert("There are no contacts to export.");
        return;
    }
    
    fetch('/api/json-to-excel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ contacts: parsedContacts })
    })
    .then(async response => {
        if (!response.ok) {
            let errorMsg = 'Export failed.';
            try {
                const data = await response.json();
                if (data && data.error) errorMsg = data.error;
            } catch (e) {}
            throw new Error(errorMsg);
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'contacts_converted.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(err => {
        alert('Failed to generate Excel file: ' + err.message);
        console.error(err);
    });
}

// -------------------------------------------------------------
// EXCEL TO VCF FLOW
// -------------------------------------------------------------

function handleExcelFile(file) {
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        showExcelError('Please upload a valid Excel spreadsheet (.xlsx or .xls).');
        return;
    }
    
    hideElement('excel-error');
    hideElement('excel-mapper-area');
    showElement('excel-loading');
    
    selectedExcelFile = file;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/excel-to-json', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideElement('excel-loading');
        if (data.error) {
            showExcelError(data.error);
        } else {
            renderMappingInterface(data.headers, data.preview, data.auto_mapping);
            showElement('excel-mapper-area');
        }
    })
    .catch(err => {
        hideElement('excel-loading');
        showExcelError('An error occurred. Make sure the backend server is running.');
        console.error(err);
    });
}

function showExcelError(msg) {
    const errorEl = document.getElementById('excel-error');
    errorEl.querySelector('.alert-message').textContent = msg;
    errorEl.classList.remove('hidden');
}

function resetExcelUpload() {
    selectedExcelFile = null;
    excelFileInput.value = '';
    hideElement('excel-mapper-area');
}

// Render column mapping interface rows
function renderMappingInterface(headers, preview, autoMapping) {
    const tbody = document.getElementById('mapping-table-body');
    tbody.innerHTML = '';
    
    headers.forEach(header => {
        const tr = document.createElement('tr');
        
        // 1. Header Name
        const nameTd = document.createElement('td');
        nameTd.innerHTML = `<strong>${header}</strong>`;
        tr.appendChild(nameTd);
        
        // 2. Preview Cell (Display data from the first sample row)
        const previewTd = document.createElement('td');
        let sampleVal = '';
        if (preview && preview.length > 0) {
            sampleVal = preview[0][header] || '';
        }
        
        const badge = document.createElement('span');
        badge.className = 'sample-data-badge';
        badge.textContent = sampleVal ? sampleVal : '— Empty Row —';
        badge.title = sampleVal;
        previewTd.appendChild(badge);
        tr.appendChild(previewTd);
        
        // 3. Mapping Dropdown Selector
        const selectTd = document.createElement('td');
        const select = document.createElement('select');
        select.className = 'mapping-select';
        select.dataset.header = header;
        
        // Populate select options
        mappingOptions.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = opt.text;
            select.appendChild(option);
        });
        
        // Set auto selected item if identified
        const suggested = autoMapping[header] || '';
        select.value = suggested;
        
        selectTd.appendChild(select);
        tr.appendChild(selectTd);
        
        tbody.appendChild(tr);
    });
}

// Submit mapping and trigger VCF download
function convertExcelToVcf() {
    if (!selectedExcelFile) {
        alert("Please upload an Excel file first.");
        return;
    }
    
    // Collect mappings
    const mapping = {};
    const selects = document.querySelectorAll('.mapping-select');
    let hasMapping = false;
    
    selects.forEach(select => {
        const header = select.dataset.header;
        const target = select.value;
        if (target) {
            mapping[header] = target;
            hasMapping = true;
        }
    });
    
    if (!hasMapping) {
        alert("Please map at least one column to a contact field.");
        return;
    }
    
    showElement('excel-loading');
    hideElement('excel-mapper-area');
    
    const formData = new FormData();
    formData.append('file', selectedExcelFile);
    formData.append('mapping', JSON.stringify(mapping));
    
    fetch('/api/excel-to-vcf', {
        method: 'POST',
        body: formData
    })
    .then(async response => {
        hideElement('excel-loading');
        if (!response.ok) {
            let errorMsg = 'Conversion failed. Please verify your file contents.';
            try {
                const data = await response.json();
                if (data && data.error) errorMsg = data.error;
            } catch (e) {}
            throw new Error(errorMsg);
        }
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = selectedExcelFile.name.replace(/\.[^/.]+$/, "") + ".vcf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
        // Bring back the mapper interface for further adjustments
        showElement('excel-mapper-area');
    })
    .catch(err => {
        hideElement('excel-loading');
        showElement('excel-mapper-area');
        alert("Error converting file: " + err.message);
        console.error(err);
    });
}
