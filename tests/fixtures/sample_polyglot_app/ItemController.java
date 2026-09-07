package com.example.demo;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ItemController {

    @GetMapping("/api/v1/catalog/items")
    public String getCatalogItems() {
        return "items";
    }
}
