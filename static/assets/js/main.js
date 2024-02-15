var msh = document.getElementById("msh")
        var myModal = new bootstrap.Modal(document.getElementById('uploadModal'))
        // myModal.show()
        var uploadGalleryBtn = document.getElementById("uploadGalleryBtn")
        var uploadForm = document.getElementById("formSubmit")
        uploadGalleryBtn.onclick = (e)=>{
             e.preventDefault()
             uploadForm.submit()
             myModal.hide()
        }
        var allImage = document.getElementsByClassName("img-container")
        var tempModal = document.getElementById("modalFillId")
        var modalPreview = new bootstrap.Modal(document.getElementById("previewModal"))


        Array.from(allImage).forEach((item)=>{
            item.onclick = (e)=>{
                let inpuIdValue = document.getElementById("imageIdInput")
                let img_id = item.id.split("img_c_")[1]
                inpuIdValue.setAttribute("value",img_id)

                tempModal.innerHTML = item.innerHTML
                let delBtn = document.createElement("button")
                delBtn.classList.add("btn")
                delBtn.classList.add("btn-danger")
                delBtn.classList.add("mt-3")
                delBtn.setAttribute("type","submit")

                let textContent = document.createTextNode("Delete")
                delBtn.appendChild(textContent)

                tempModal.appendChild(inpuIdValue)
                tempModal.appendChild(delBtn)
                modalPreview.show()
            }
        })